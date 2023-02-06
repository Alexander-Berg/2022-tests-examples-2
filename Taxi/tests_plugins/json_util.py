class VarHook:
    def __init__(self, variables):
        self.variables = variables

    def __call__(self, obj):
        if '$var' in obj:
            varname = obj['$var']
            if varname in self.variables:
                return self.variables[varname]
            if '$default' in obj:
                return obj['$default']
            raise RuntimeError('Unknown variable name %s' % (varname,))
        return obj
