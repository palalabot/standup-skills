import handler as h

def bad(inp):
    try: h.validate(inp)
    except ValueError: return True
    return False

assert h.validate({"action": "embed", "texts": ["hi"]}) == ("embed", ["hi"])
assert h.validate({"action": "similarity", "a": "x", "b": "y"}) == ("similarity", ["x", "y"])
assert bad(None) and bad({}) and bad({"action": "drop"})
assert bad({"action": "embed", "texts": []}) and bad({"action": "embed", "texts": [1]})
assert bad({"action": "embed", "texts": ["a"] * 65}) and bad({"action": "embed", "texts": ["a" * 8001]})
assert bad({"action": "similarity", "a": "", "b": "y"})
assert h.handler({"input": {"action": "x"}}) == {"error": "action must be 'embed' or 'similarity'"}
print("ok")
