# rctf 2018 cpushop

Shout out to Gnu3duck5 and clampz!

We are given a python file `cpushop.py` and the address of a server which runs `cpushop.py` when you connect.
When you first run `cpushop` we are presented with a menu:

```
CPU Shop
Money: $1530
1. List Items
2. Order
3. Pay
4. Exit
```

After each command (besides exit), you are returned to the menu.
We can list the cpuz for sale:

```
Command: 1
 0 - Intel Core i9-7900X           $999
 1 - Intel Core i7-7820X           $599
 2 - Intel Core i7-7700K           $349
 3 - Intel Core i5-7600K           $249
 4 - Intel Core i3-7350K           $179
 5 - AMD Ryzen Threadripper 1950X  $999
 6 - AMD Ryzen 7 1800X             $499
 7 - AMD Ryzen 5 1600X             $249
 8 - AMD Ryzen 3 1300X             $149
 9 - Flag                          $99999
```

And order a cpu:
```
Command: 2
Product ID: 5
Your order:
product=AMD Ryzen Threadripper 1950X&price=999&timestamp=1526865369263614&sign=8ec4caf18691523024d395216d1595ef398e306609840952240b05177fdbcee5
```

We are given an `order` string which encodes the order parameters as a url query string.
We use this string when we pay:

```
  Command: 3
  Your order:
  product=AMD Ryzen Threadripper 1950X&price=999&timestamp=1526865369263614&sign=8ec4caf18691523024d395216d1595ef398e306609840952240b05177fdbcee5
  Your current money: $531
  You have bought AMD Ryzen Threadripper 1950X
```

It is clear that 
  * We need to buy the "Flag" product.
  * The flag product is way too expensive for us to afford.
  * The `order` string encodes the name of the `product`, its `price`, and is cryptographically `sign`ed
  * We need to forge a signed `order` with a lower price.

Let's now look at the code for `cpushop.py`

On line `14` we see that `signkey` is a random alphanumeric string of length between 8 and 32.

```python
signkey = ''.join([random.choice(string.letters+string.digits) for _ in xrange(random.randint(8,32))])
```

On line `28-29` in the `order` method we see that a new order is signed using the following scheme:
```python
sign = sha256(signkey+payment).hexdigest()
payment += '&sign=%s' % sign
```

This scheme is vulnerable to [length extension attack](https://en.wikipedia.org/wiki/Length_extension_attack).
A `sha256` hash is not intended to be used as a message authentication code as it is here in `cpushop`.
Given only a `message`, the signature of the message (i.e. `sha256(key + message)`), and the length of the `key`, we use this attack to concatenate onto the original message and find the signature of this new message without knowing the key.
Since we don't know the length of the `key`, except that it's between 8 and 32, we can attempt to forge an `order` for each of these lengths.

On lines `36-48` of the `pay` function we see the order query string is split into the signature (i.e. `sign`) and the rest of the parameters (i.e. `payment`).
```python
payment = raw_input().strip()
sp = payment.rfind('&sign=')
if sp == -1:
    print 'Invalid Order!'
    return
sign = payment[sp+6:]
try:
    sign = sign.decode('hex')
except TypeError:
    print 'Invalid Order!'
    return

payment = payment[:sp]
```
Then we see in lines `50-52` that the query string sans the signature is signed, and compared to the signature that was in the order.

```python
if signchk != sign:
    print 'Invalid Order!'
    return
```

In the `pay` function method on lines `54-62` we see that the parameters in the `order` url query string are iterated over and the price and product values are set.
```python
for k,v in parse_qsl(payment):
    if k == 'product':
        product = v
    elif k == 'price':
        try:
            price = int(v)
        except ValueError:
            print 'Invalid Order!'
            return
```
Therefore, if we append `&price=1` to the parameters the `price` variable will be overwritten.

In `cpushop_solution.py` we implement this attack using the `hashpumpy` library and the function `hashpump`.
The function `modify` is the interesting part of the solution.
`modify` takes a signed order string, and creates a new singned order string with `&price=1` concatenated to the parameters.
```python
def modify(o, key_len):
  split = '&sign='
  index = o.find(split)
  signature = o[index + len(split):]
  message = o[:index]
  new_signature, modified_message =  hashpump(signature, message, '&price=1', key_len)
  return modified_message + split + new_signature
```
The rest of the program connects to the service, `order`s the "Flag" product, then for each possible key length, calls `modify` to forge a flag order string to set the price to 1, and attempts to `pay` using this forged order.

Running the program we get
```
❯ python cpushop_solution.py
[+] Opening connection to cpushop.2018.teamrois.cn on port 43000: Done
[+] Finding flag: RCTF{ha5h_l3ngth_ex7ens10n_a77ack_1s_ez}
[*] Closed connection to cpushop.2018.teamrois.cn port 43000
```

Thanks for reading!
