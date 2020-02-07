## Run this in the directory with the .so files built by calling setup.py
import my_custom_iterator
import io

## https://docs.python.org/3/library/io.html#binary-i-o

def interop_example():
  f = io.open("app.py", "rb", buffering=0)
  itr = my_custom_iterator.MyRangeIterator(2,5)

  data = f.read(100)  ## https://docs.python.org/3/library/io.html#io.RawIOBase.read
  if(data is not None):
    itr.add_bytes(data)
  itr.next()
  itr.next()


## For async: see listening to sockets in non-blocking mode https://docs.python.org/3/library/socket.html#socket.socket.setblocking
## see also https://docs.python.org/2/howto/sockets.html#non-blocking-sockets
