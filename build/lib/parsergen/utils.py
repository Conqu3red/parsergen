def RequiredAttributes(*required_attrs):
    "https://stackoverflow.com/a/22047600"
    class RequiredAttributesMeta(type):
        def __init__(cls, name, bases, attrs):
            missing_attrs = ["'%s'" % attr for attr in required_attrs 
                             if not hasattr(cls, attr)]
            if missing_attrs:
                raise AttributeError("class '%s' requires attribute%s %s" %
                                     (name, "s" * (len(missing_attrs) > 1), 
                                      ", ".join(missing_attrs)))
    return RequiredAttributesMeta