import imaplib
import email
from dateutil.parser import parse
from email.header import decode_header
import requests
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Función para enviar una respuesta por correo electrónico


def send_response(sender_email, missing_fields):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    smtp_user = "correodeprueb36@gmail.com"
    smtp_password = "oihc vtci zdow kqnq"

    # Crear el mensaje
    msg = MIMEMultipart()
    msg['From'] = smtp_user
    msg['To'] = sender_email
    msg['Subject'] = "Información faltante para abrir el ticket"

    body = f"""
    Estimado usuario,

    Hemos recibido su correo electrónico, pero faltan algunos datos necesarios para abrir el ticket. A continuación, se indican los campos que faltan:

    {', '.join(missing_fields)}

    Por favor, asegúrese de incluir los siguientes campos en su correo:
    - cuit: (por ejemplo: 32323232321)
    - n° de maquina: (por ejemplo: 32)
    - area: (por ejemplo: finanzas)
    - tipo de problema: (por ejemplo: hardware)
    - descripcion: (detalles del problema)

    Ejemplo de estructura del correo:
    cuit: 32323232321
    n° de maquina: 32
    area: finanzas
    tipo de problema: hardware
    descripcion: [Descripción del problema]

    Gracias por su cooperación.

    Atentamente,
    Su equipo de soporte
    """

    msg.attach(MIMEText(body, 'plain'))

    # Enviar el correo
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.sendmail(smtp_user, sender_email, msg.as_string())


def split_name_email(datos: str):
    partes = datos.split('<')
    name = partes[0].strip()
    email = partes[1].rstrip('>')

    # Validación básica del correo electrónico
    # if not re.match(r"[^@]+@[^@]+\.[^@]+", email):
    #     raise ValueError("Dirección de correo electrónico inválida")

    return name, email


def __connect_to_imap_server(host, port, username, password):
    """Conecta al servidor IMAP y devuelve una conexión."""
    mail = imaplib.IMAP4_SSL(host, port)
    mail.login(username, password)
    return mail


def __fetch_unread_emails(mail):
    """Obtiene los IDs de los correos electrónicos no leídos."""
    status, messages = mail.search(None, 'UNSEEN')
    return messages[0].split()


def __parse_email(msg):
    """Parsea un mensaje de correo electrónico y extrae los datos relevantes."""
    subject, encoding = decode_header(msg["Subject"])[0]

    if isinstance(subject, bytes):
        subject = subject.decode(encoding or "utf-8")
    sender_name, sender_email = split_name_email(msg.get("From"))
    date_object = parse(msg.get("Date"))
    formato = "%Y-%m-%d %H:%M:%S"
    created_date = date_object.strftime(formato)

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body = part.get_payload(decode=True).decode()
    else:
        body = msg.get_payload(decode=True).decode()

    # Eliminar líneas vacías adicionales
    body = "\n".join([line.strip()
                     for line in body.splitlines() if line.strip()])

    # Define regular expressions for each data point ensuring we stop at the next field
    cuit_match = re.search(
        r'cuit:\s*(.*?)(?=\s+n° de maquina:|$)', body, re.IGNORECASE)
    nro_maquina_match = re.search(
        r'n° de maquina:\s*(.*?)(?=\s+área:|$)', body, re.IGNORECASE)
    area_match = re.search(
        r'área:\s*(.*?)(?=\s+tipo de problema:|$)', body, re.IGNORECASE)
    tipo_problema_match = re.search(
        r'tipo de problema:\s*(.*?)(?=\s+descripción:|$)', body, re.IGNORECASE)
    descripcion_match = re.search(
        r'descripción:\s*(.*)', body, re.IGNORECASE | re.DOTALL)

    # Extract data if matches are found
    cuit = cuit_match.group(1).strip() if cuit_match else None
    nro_maquina = nro_maquina_match.group(
        1).strip() if nro_maquina_match else None
    area = area_match.group(1).strip() if area_match else None
    tipo_problema = tipo_problema_match.group(
        1).strip() if tipo_problema_match else None
    descripcion = descripcion_match.group(
        1).strip() if descripcion_match else None

    missing_fields = []
    if not cuit:
        missing_fields.append("cuit")
    if not nro_maquina:
        missing_fields.append("n° de maquina")
    if not area:
        missing_fields.append("area")
    if not tipo_problema:
        missing_fields.append("tipo de problema")
    if not descripcion:
        missing_fields.append("descripcion")

    return body, subject, descripcion, sender_name, sender_email, created_date, cuit, nro_maquina, area, tipo_problema, missing_fields


def __create_ticket(subject, body, sender_name, sender_email, created_date, cuit, nro_maquina, area, tipo_problema):
    """Crea un ticket enviando una solicitud POST a la API."""
    ticket_data = {
        "subject": subject,
        "description": body,
        "sender_email": sender_email,
        "sender_name": sender_name,
        "cuit": cuit,
        "num_machine": nro_maquina,
        "type_problem": tipo_problema,
        "area": area,
        "created_at": created_date,
    }
    requests.post("http://localhost:8000/tickets/", json=ticket_data)


def check_emails():
    """Revisa los correos electrónicos no leídos y crea tickets."""
    mail = __connect_to_imap_server(
        "imap.gmail.com", 993, "correodeprueb36@gmail.com", "oihc vtci zdow kqnq")
    mail.select("inbox")
    email_ids = __fetch_unread_emails(mail)

    for email_id in email_ids:
        status, msg_data = mail.fetch(email_id, "(RFC822)")
        for response_part in msg_data:
            if isinstance(response_part, tuple):
                msg = email.message_from_bytes(response_part[1])
                body, subject, description, sender_name, sender_email, created_date, cuit, nro_maquina, area, tipo_problema, missing_fields = __parse_email(
                    msg)

                if missing_fields:
                    send_response(sender_email, missing_fields)
                else:
                    print(f"CUIT: {cuit}")
                    print(f"N° Maquina: {nro_maquina}")
                    print(f"Area: {area}")
                    print(f"Tipo Problema: {tipo_problema}")
                    print(f"Descripcion: {description}")
                    __create_ticket(subject, description, sender_name,
                                    sender_email, created_date, int(cuit), int(nro_maquina), area, tipo_problema)
