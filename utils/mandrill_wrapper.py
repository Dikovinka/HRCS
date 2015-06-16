__author__ = 'Max'
import mandrill
from HRMS.settings import MANDRILL_API_KEY
mandrill_client = mandrill.Mandrill(MANDRILL_API_KEY)

def send_mail(template_name, email_to, context):
    message = {
        'to': [],
        'global_merge_vars': []
    }
    for em in email_to:
        message['to'].append({'email': em})

    for k, v in zip(context.keys(), context.values()):
        message['global_merge_vars'].append(
            {"name": k, "content": v}
        )
    mandrill_client.messages.send_template(template_name, [], message)