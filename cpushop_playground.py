from pwn import process, remote, context, log
from hashpumpy import hashpump
from string import letters, digits
from random import choice
from hashlib import sha256

def make_key():
  return ''.join([choice(letters + digits) for _ in xrange(8,32)])

def sign(message, key):
  return sha256(key + message).hexdigest()

def check(message, signature, key):
  return sign(message, key) == signature

def playground():
  key = make_key()
  message = 'hello, world'
  s1 = sign(message, key)

  #s2 = sign(message + ' foo', key)

  def thing(message, signature):
    if check(message, signature, key):
      print 'This was signed by me :)'
    else:
      print 'This was not signed by me >:( '

  # correctly determines when message was signed with key
  thing(message, s1)
  # detects when you modified the message
  thing(message + ' give me money!', s1)
  
  # doesn't detect modifed message when using length extension attack with known key length
  s2, modified_message = hashpump(s1, message, ' foo', len(key))
  thing(modified_message, s2)

  # brute force the key length
  for n in xrange(8, 32):
    s2, modified_message = hashpump(s1, message, ' foo', n)
    thing(modified_message, s2)

if __name__ == '__main__':
  playground()

