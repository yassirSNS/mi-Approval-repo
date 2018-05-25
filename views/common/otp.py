import urllib2
from random import randint

REGISTRATION = 1
PASSWORD = 2
OTHERS = 3


def generate_otp():
    n = randint(0, 9999)
    if n == 0:
        otp = '0000'
    elif n < 10:
        otp = '000{}'.format(n)
    elif n < 100:
        otp = '00{}'.format(n)
    elif n < 1000:
        otp = '0{}'.format(n)
    else:
        otp = str(n)

    return otp


def send_otp(mobile, otp, otp_type=OTHERS):
    link = 'http://smsgateway.me/api/v3/messages/send/variable?email=viki73bhardwaj@gmail.com' \
           '&password=rubryxnet123&device=76140&number={}&message={}'

    if otp_type == REGISTRATION:
        message = '{}%20is%20the%20OTP%20for%20your%20mi-Approval%20registration'.format(otp)
    elif otp_type == PASSWORD:
        message = '{}%20is%20the%20OTP%20for%20your%20mi-Approval%20password%20reset'.format(otp)
    else:
        message = '{}%20is%20the%20OTP%20for%20your%20mi-Approval%20account'.format(otp)

    link = link.format(mobile, message)

    urllib2.urlopen(link)
    # f = urllib2.urlopen(link)
    # print f.read(500)
