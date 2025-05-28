# 🔒 PDF Protector – Proteja seus PDFs contra cópia e uso indevido

Este projeto é uma aplicação web desenvolvida com **Flask** que permite ao usuário enviar arquivos PDF e aplicar diversas **camadas de proteção** contra pirataria.

**A aplicação pode ser acessada em:** https://pdfprotector-1b2c.onrender.com/

## 🚀 Funcionalidades

- ✅ Upload de arquivos PDF
- ✅ Adição de marca d’água com nome, e-mail, CPF ou texto personalizado
- ✅ Proteção com senha
- ✅ Inserção de metadados (título, autor, assunto, palavras-chave)
- ✅ Restrições de permissões: impedir impressão, cópia e edição
- ✅ Geração de PDF final protegido e pronto para download

## ⚙️ Tecnologias utilizadas

- [Python 3](https://www.python.org/)
- [Flask](https://flask.palletsprojects.com/)
- [PyPDF2](https://pypdf2.readthedocs.io/en/3.x/)
- [pikepdf](https://pikepdf.readthedocs.io/)
- [WTF Forms](https://wtforms.readthedocs.io/en/3.2.x/)
- HTML5 + CSS3 + JS
- Jinja2 (templates)

## 📁 Estrutura do projeto

```
pdf-protector/
│
├── app.py                (Arquivo principal da aplicação Flask)
├── pdf_modifier.py       (Lógica de modificação e proteção dos arquivos PDF)
├── templates/            (Templates HTML renderizados pelo Flask)
│   └── index.html        (Página principal da aplicação)
├── static/               (Arquivos estáticos como CSS, favicon e imagens)
│   ├── css/              (Folhas de estilo da aplicação)
│   ├── favicon/          (Ícones do site)
│   └── images/           (Imagens usadas na interface)
├── uploads/              (Pasta para arquivos enviados pelos usuários - estes são excluídos da pasta logo após as requisições POST)
├── requirements.txt      (Lista de dependências Python do projeto)
├── .env                  (Variáveis de ambiente, como a SECRET_KEY)
└── .gitignore            (Arquivos e pastas ignorados pelo Git)
```

## ✉️ Contato
Para dúvidas ou sugestões, entre em contato:
- 📧 sabrinaoliveira030989@gmail.com