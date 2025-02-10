# arquivo: email_handler.py
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailHandler:
    def __init__(self, smtp_server, port, username, password):
        self.smtp_server = smtp_server
        self.port = port
        self.username = username
        self.password = password
        self.server = None

    def connect(self):
        try:
            self.server = smtplib.SMTP(self.smtp_server, self.port)
            self.server.starttls()
            self.server.login(self.username, self.password)
            print("Conexão com o servidor SMTP realizada com sucesso!")
        except Exception as e:
            print(f"Erro ao conectar ao servidor SMTP: {e}")
            self.server = None

    def send_email(self, subject, body, from_email, to_email):
        if not self.server:
            print("Servidor SMTP não conectado. Chame o método 'connect' primeiro.")
            return

        try:
            msg = MIMEMultipart()
            msg['From'] = from_email
            msg['To'] = to_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            self.server.sendmail(from_email, to_email, msg.as_string())
            print("E-mail enviado com sucesso!")
        except Exception as e:
            print(f"Erro ao enviar e-mail: {e}")

    def disconnect(self):
        if self.server:
            self.server.quit()
            print("Conexão com o servidor SMTP encerrada.")

