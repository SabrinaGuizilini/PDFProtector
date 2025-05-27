from flask import Flask, render_template, request, send_file, flash, redirect, url_for, after_this_request
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import StringField, SubmitField, SelectField, BooleanField, PasswordField, ValidationError
from wtforms.widgets import ColorInput
import os
import threading
import time
from dotenv import load_dotenv
from pdf_modifier import modify_pdf

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['UPLOAD_FOLDER'] = './uploads/'

class PDFInputForm(FlaskForm):
    arquivo_pdf = FileField()
    chk_watermark = BooleanField("Marca d'água")
    chk_password = BooleanField('Senha')
    chk_metadata = BooleanField('Metadados')
    chk_permissions = BooleanField('Permissões')
    password_pdf = PasswordField('Insira a senha para o PDF:')
    watermark_text = StringField("Texto:")
    watermark_color = StringField('Cor:', widget=ColorInput())
    watermark_position = SelectField('Posicionamento na página:', choices=[('top-left', 'Top-Left'), ('top-right', 'Top-Right'), ('bottom-left', 'Bottom-Left'), ('bottom-right', 'Bottom-Right')])
    not_insert_watermark_first_page = BooleanField("Não colocar na primeira página:")
    metadatas_keys = StringField("Chaves:")
    metadatas_values = StringField("Valores:")
    block_printing = BooleanField('Bloquear impressão:')
    block_copy = BooleanField('Bloquear cópia de texto/imagens:')
    block_editing = BooleanField('Bloquear edição:')
    submit = SubmitField('Proteger PDF')

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators):
            return False

        if not (self.chk_watermark.data or self.chk_password.data or self.chk_metadata.data or self.chk_permissions.data):
            self.form_errors = ['Você deve selecionar pelo menos uma opção de proteção.']
            return False

        return True
    
    def validate_arquivo_pdf(self, field):
        if not field.data:
            raise ValidationError("Você precisa selecionar um arquivo PDF.")
        if not hasattr(field.data, 'filename') or not field.data.filename.lower().endswith('.pdf'):
            raise ValidationError("O arquivo selecionado não é um PDF válido.")

    def validate_watermark_text(self, field):
        if self.chk_watermark.data:
            if not field.data or not field.data.strip():
                raise ValidationError("O texto da marca d'água é obrigatório.")
            if len(field.data.strip()) > 30:
                raise ValidationError("O texto da marca d'água deve ter no máximo 30 caracteres.")

    def validate_password_pdf(self, field):
        if self.chk_password.data:
            if not field.data or not field.data.strip():
                raise ValidationError("A senha do PDF é obrigatória.")

    def validate_metadatas_keys(self, field):
        if self.chk_metadata.data:
            keys = [k.strip() for k in (field.data or '').split(';') if k.strip()]
            if not keys:
                raise ValidationError("As chaves de metadados são obrigatórias.")
            self._metadata_keys = keys

    def validate_metadatas_values(self, field):
        if self.chk_metadata.data:
            values = [v.strip() for v in (field.data or '').split(';') if v.strip()]
            if not values:
                raise ValidationError("Os valores de metadados são obrigatórios.")

            keys = getattr(self, '_metadata_keys', [])
            if keys and len(keys) != len(values):
                raise ValidationError(f'O número de chaves ({len(keys)}) é diferente do número de valores ({len(values)}).')
    
    
def delayed_file_remove(path, delay=5):
    def _remove():
        time.sleep(delay)
        try:
            os.remove(path)
        except Exception as e:
            app.logger.error(f"Erro ao excluir o arquivo (atrasado): {e}")
    threading.Thread(target=_remove).start()
    

@app.route('/', methods=['GET', 'POST'])
def index():
    form = PDFInputForm()
    if form.validate_on_submit():
        file = request.files['arquivo_pdf']
        filename = secure_filename(file.filename)
        path_file = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(path_file)
        
        @after_this_request
        def remove_file(response):
            delayed_file_remove(path_file, delay=5)
            return response

        try:
            modify_pdf(
                input_pdf_path=path_file,
                chk_watermark=form.chk_watermark.data,
                chk_password=form.chk_password.data,
                chk_metadata=form.chk_metadata.data,
                chk_permissions=form.chk_permissions.data,
                password_pdf=form.password_pdf.data,
                watermark_text=form.watermark_text.data,
                watermark_color=form.watermark_color.data,
                watermark_position=form.watermark_position.data,
                not_insert_watermark_first_page=form.not_insert_watermark_first_page.data,
                metadatas_keys=form.metadatas_keys.data,
                metadatas_values=form.metadatas_values.data,
                block_printing=form.block_printing.data,
                block_copy=form.block_copy.data,
                block_editing=form.block_editing.data
            )
            return send_file(path_file, as_attachment=True)
        except Exception as e:
            flash('Falha ao processar o arquivo: ' + str(e))
            return redirect(request.url)

    return render_template('index.html', form=form)
