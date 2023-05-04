import json

def json_safe(d):
    """
    Return only the JSON-safe part of d(a python dict object).

    Used to emulate reading data through a serialization straw.

    """
    # pylint: disable=invalid-name

    # six.binary_type is here because bytes are sometimes ok if they represent valid utf8
    # so we consider them valid for now and try to decode them with decode_object.  If that
    # doesn't work they'll get dropped later in the process.
    ok_types = (type(None), int, float, bytes, str, list, tuple, dict)

    def decode_object(obj):
        """
        Convert an object to a JSON serializable form by decoding all byte strings.

        In particular if we find any byte strings try to convert them to
        utf-8 strings.  If we run into byte strings that can't be decoded as utf8 strings
        throw an exception.

        For other non-serializable objects we return them as is.

        raises: Exception
        """
        if isinstance(obj, bytes):
            return obj.decode('utf-8')
        if isinstance(obj, (list, tuple)):
            new_list = []
            for i in obj:
                new_obj = decode_object(i)
                new_list.append(new_obj)
            return new_list
        if isinstance(obj, dict):
            new_dict = {}
            for k, v in obj.items():
                new_key = decode_object(k)
                new_value = decode_object(v)
                new_dict[new_key] = new_value
            return new_dict
        return obj

    bad_keys = ("__builtins__",)
    jd = {}
    for k, v in d.items():
        if not isinstance(v, ok_types):
            continue
        if k in bad_keys:
            continue
        try:
            # Python's JSON encoder will produce output that
            # the JSON decoder cannot parse if the input string
            # contains unicode "unpaired surrogates" (only on Linux)
            # To test for this, we try decoding the output and check
            # for a ValueError
            v = json.loads(json.dumps(decode_object(v)))

            # Also ensure that the keys encode/decode correctly
            k = json.loads(json.dumps(decode_object(k)))
        except Exception:  # pylint: disable=broad-except
            continue
        else:
            jd[k] = v
    return json.loads(json.dumps(jd))


def read_globals_from_file():
    with open('untrusted_code/globals.in.json') as globals_infile:
        return json.load(globals_infile)

def write_globals_to_file(globals_dict):
    with open('untrusted_code/globals.out.json', 'w') as globals_outfile:
        json.dump(json_safe(globals_dict), globals_outfile)
