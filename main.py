## main.py
## Load ASB without exposing sensitive code.
# Written for Micropython.

__version__ = "0.0.1"

def load_asb():
    print("Loading AutoSecurityBox...")
    import asb

if __name__ == "__main__":
    load_asb()
