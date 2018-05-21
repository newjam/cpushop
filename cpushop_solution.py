from pwn import process, remote, context, log
from hashpumpy import hashpump
from string import letters, digits
from random import choice
from hashlib import sha256

def order(io, p_id):
  io.recvuntil('Command: ')
  io.sendline(str(2))
  io.recvuntil('Product ID: ')
  io.sendline(str(p_id))
  io.recvuntil('Your order:\n')
  o = io.recvline()[:-1]
  return o

def pay(io, o):
  io.recvuntil('Command: ')
  io.sendline('3')
  io.recvuntil('Your order:') # remote uses this
  # io.recvuntil('Your order:\n') # local uses this
  io.sendline(o)

  r = io.recvline()[:-1]
  if r.startswith('Invalid Order!'):
    raise Exception(r)
  if r == 'Go away you poor bastard!':
    raise Exception(r)

  money = int(r[len('Your current money: $'):])
  io.recvuntil('You have bought ')
  product = io.recvline()[:-1]
  if product == 'Flag':
    io.recvuntil('Good job! Here is your flag: ')
    flag = io.recvline()[:-1]
    return money, product, flag
  return money, product, None

def connect():
  #return remote('cpushop.2018.teamrois.cn', 43000)
  return process(['python', './cpushop.py'])

def modify(o, key_len):
  split = '&sign='
  index = o.find(split)
  signature = o[index + len(split):]
  message = o[:index]
  new_signature, modified_message =  hashpump(signature, message, '&price=1', key_len)
  return modified_message + split + new_signature

def main():
  context.log_level = 'info'
  io = connect()
  o = order(io, 9)
  log.debug('Original Order:', o)
  progress = log.progress('Finding flag')
  for key_len in xrange(8, 32):
    progress.status('Trying key length of ' + str(key_len))
    modified = modify(o, key_len)
    log.debug('Modified Order:', modified)
    try:
      m, p, flag = pay(io, modified)
      progress.success(flag)
      break
    except Exception as e:
      progress.status('Key length ' + str(key_len) + ' failed: ' + str(e))
  io.close()

if __name__ == '__main__':
  main()

