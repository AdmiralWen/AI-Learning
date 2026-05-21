# Example of a locally hosted MCP server, where you can develop and test your own tools.
# Tools are just regular Python functions. To expose them to your agent, use the @mcp.tool() decorator.
# Each tool should:
#     - Have type hints (so MCP can generate the interface)
#     - Include a simple docstring (so humans + agents know what it does)

from random import randrange

# Set up mcp server using FastMCP, name it 'DemoServer'.
#from mcp.server.fastmcp import FastMCP
from fastmcp import FastMCP
mcp = FastMCP('PrimeTools')

# Define some tools and expose them to the server.
@mcp.tool()
def is_prime(n: int, k: int = 7) -> bool:
    '''
    Stochastic primality test based on Rabin-Miller algorithm. If function returns False, the number is composite.
    If function returns True, the number is prime with a very high probability. Set the argument k to be the number
    of trials to perform (default is k = 7).
    '''
    if n < 2: return False
    for i in(2, 3, 5, 7):
        if n == i: return True
        elif n % i == 0: return False

    r, s = 0, n-1
    while s % 2 == 0:
        r += 1
        s //= 2

    for _trial in range(k):
        a = randrange(2, n-1)
        x = pow(a, s, n)
        if x == 1 or x == n-1:
            continue
        for _j in range(r-1):
            x = pow(x, 2, n)
            if x == n-1:
                break
        else:
            return False

    return True

@mcp.tool()
def get_prime_factors(n: int) -> list[int]:
    '''
    Returns the list of prime factors of a given number n.
    '''
    i = 2
    factors = []
    # Loop until the divisor squared is greater than n
    while i * i <= n:
        if n % i:
            i += 1
        else:
            n //= i
            factors.append(i)
    if n > 1:
        factors.append(n)
    return factors


# Finally, we run the server. By default, it will run locally and communicate over stdio. Once we
# have this, we can start the server by running the .py file in terminal `python mcp_server_local.py`, or
# if using the CLI, then `fastmcp run server.py –transport http –port 8000`
if __name__ == "__main__":
    # Run server locally (default option, 'stdio'):
    # In our case, stdio doesn't work when using terminal.
    #mcp.run(transport='stdio')

    # Or run over HTTP if you want to run it on cloud or over a network:
    mcp.run(transport="http", host="127.0.0.1", port=8000)