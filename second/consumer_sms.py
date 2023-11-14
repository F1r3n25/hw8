import json

import pika

from mongoengine import connect, Document, StringField, BooleanField
from first.password import PASS_


connect(host=f"mongodb+srv://dmitriy_test:{PASS_}@homework8.21evbba.mongodb.net/?retryWrites=true&w=majority", ssl=True)


class Contact(Document):
    full_name = StringField(required=True)
    email = StringField(required=True)
    is_sent = BooleanField(default=False)
    phone_number = StringField(required=True)
    preferred_contact_method = StringField(choices=["email", "sms"], default="email")



def main():
    credentials = pika.PlainCredentials('guest', 'guest')
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host='localhost', port=5672, credentials=credentials))
    channel = connection.channel()

    sms_queue_name = 'sms_contacts_queue'
    channel.queue_declare(queue=sms_queue_name, durable=True)

    def send_email(contact_id):
        print(f"Email sent to contact with ID: {contact_id}")
        contact = Contact.objects.get(id=contact_id)
        contact.is_sent = True
        contact.save()

    def callback(ch, method, properties, body):
        message = json.loads(body.decode())
        contact_id = message['contact_id']
        send_email(contact_id)
        print(f"Callback function executed for contact with ID: {contact_id}")

    channel.basic_consume(queue=sms_queue_name, on_message_callback=callback, auto_ack=True)
    print('Waiting for messages. To exit press CTRL+C')
    channel.start_consuming()


if __name__ == '__main__':
    main()
