"""Utilitário para envio de emails"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_password_reset_email(to_email, reset_url, user_name=None):
    """
    Envia email de recuperação de senha
    
    Args:
        to_email: Email do destinatário
        reset_url: URL para redefinir a senha
        user_name: Nome do usuário (opcional)
    
    Returns:
        bool: True se enviado com sucesso, False caso contrário
    """
    # Verifica se as configurações de email estão definidas
    if not Config.MAIL_USERNAME or not Config.MAIL_PASSWORD:
        print(f"⚠️ Configurações de email não definidas. Link de recuperação: {reset_url}")
        return False
    
    try:
        # Cria a mensagem
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Recuperação de Senha - RecipeApp'
        msg['From'] = Config.MAIL_FROM
        msg['To'] = to_email
        
        # Nome do usuário ou tratamento genérico
        greeting = f"Olá, {user_name}!" if user_name else "Olá!"
        
        # Corpo do email em texto simples
        text = f"""
{greeting}

Você solicitou a recuperação de senha para sua conta no RecipeApp.

Clique no link abaixo para redefinir sua senha:
{reset_url}

Este link expira em 24 horas.

Se você não solicitou esta recuperação de senha, ignore este email.

Atenciosamente,
Equipe RecipeApp
"""
        
        # Corpo do email em HTML
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
        }}
        .container {{
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .button {{
            display: inline-block;
            padding: 12px 30px;
            background-color: #e74c3c;
            color: white;
            text-decoration: none;
            border-radius: 4px;
            margin: 20px 0;
        }}
        .button:hover {{
            background-color: #c0392b;
        }}
        .footer {{
            margin-top: 30px;
            padding-top: 20px;
            border-top: 1px solid #eee;
            font-size: 12px;
            color: #666;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h2 style="color: #e74c3c;">Recuperação de Senha</h2>
        <p>{greeting}</p>
        <p>Você solicitou a recuperação de senha para sua conta no RecipeApp.</p>
        <p>Clique no botão abaixo para redefinir sua senha:</p>
        <a href="{reset_url}" class="button">Redefinir Senha</a>
        <p>Ou copie e cole este link no seu navegador:</p>
        <p style="word-break: break-all; color: #666;">{reset_url}</p>
        <p><strong>Este link expira em 24 horas.</strong></p>
        <p>Se você não solicitou esta recuperação de senha, ignore este email.</p>
        <div class="footer">
            <p>Atenciosamente,<br>Equipe RecipeApp</p>
        </div>
    </div>
</body>
</html>
"""
        
        # Adiciona as partes ao email
        part1 = MIMEText(text, 'plain', 'utf-8')
        part2 = MIMEText(html, 'html', 'utf-8')
        
        msg.attach(part1)
        msg.attach(part2)
        
        # Envia o email
        with smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT) as server:
            if Config.MAIL_USE_TLS:
                server.starttls()
            server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
            server.send_message(msg)
        
        return True
    
    except Exception as e:
        print(f"Erro ao enviar email: {str(e)}")
        return False




