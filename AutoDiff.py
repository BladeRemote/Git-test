import math as _math

class Dual:
    def __init__(self, real, dual):
        self.real = real
        self.dual = dual
    
    
    def __str__(self):
        isntreal=self.real==0
        isntdual=self.dual==0
        if isntdual:
            return f"{self.real}"
        elif self.dual==1:
            return f"{'' if isntreal else str(self.real)+'+'}ε"
        elif self.dual==-1:
            return f"{'' if isntreal else str(self.real)}-ε"
        else:
            if self.dual>0:
                return f"{'' if isntreal else str(self.real)+'+'}{self.dual}ε"
            else:
                return f"{'' if isntreal else str(self.real)}{self.dual}ε"

    def __add__(self, other):
        if isinstance(other, Dual):
            return Dual(self.real + other.real, self.dual + other.dual)
        else:
            return Dual(self.real + other, self.dual)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, Dual):
            return Dual(self.real - other.real, self.dual - other.dual)
        else:
            return Dual(self.real - other, self.dual)

    def __rsub__(self, other):
        return self.__sub__(other)*-1

    def __neg__(self):
        return Dual(-self.real, -self.dual)

    def __mul__(self, other):
        if isinstance(other, Dual):
            return Dual(self.real * other.real, self.real * other.dual + self.dual * other.real)
        else:
            return Dual(self.real * other, self.dual * other)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, Dual):
            return Dual(self.real / other.real, (self.dual * other.real - self.real * other.dual) / (other.real ** 2))
        else:
            return Dual(self.real / other, self.dual / other)
    
    def __rtruediv__(self, other):
        return other*Dual(self.real,-self.dual)/(self.real**2)
    
    def __pow__(self, other):
        if isinstance(other, Dual):
            return Dual(self.real**other.real,(other.real*self.dual/self.real+other.dual*_math.log(self.real))*self.real**other.real)
        else:
            return Dual(self.real**other, other * self.dual * self.real**(other-1))
    
    def __rpow__(self, other):
        return Dual(other**self.real,self.dual*_math.log(other)*other**self.real)


class EnhancedMath:
    def __init__(self, original_module):
        self._math = original_module
        m = original_module

        # Table of (function, derivative) pairs. Adding a new
        # differentiable function is one line here — nothing else changes.
        self._diff_rules = {
            "sqrt": (m.sqrt, lambda x: 0.5 / m.sqrt(x)),
            "sin":  (m.sin,  lambda x: m.cos(x)),
            "cos":  (m.cos,  lambda x: -m.sin(x)),
            "tan":  (m.tan,  lambda x: 1 / m.cos(x) ** 2),
            "asin": (m.asin, lambda x: 1/m.sqrt(1 - x**2)),
            "acos": (m.acos, lambda x: -1/m.sqrt(1 - x**2)),
            "atan": (m.atan, lambda x: 1/(1 + x**2)),
            "sinh": (m.sinh, lambda x: m.cosh(x)),
            "cosh": (m.cosh, lambda x: m.sinh(x)),
            "tanh": (m.tanh, lambda x: 1 - m.tanh(x)**2),
            "asinh": (m.asinh, lambda x: 1/m.sqrt(1 + x**2)),
            "acosh": (m.acosh, lambda x: 1/m.sqrt(x**2 - 1)),
            "atanh": (m.atanh, lambda x: 1/(1 - x**2)),
            "exp":  (m.exp,  lambda x: m.exp(x)),
            "log":  (m.log,  lambda x: 1 / x),
        }

        for name, (f, fprime) in self._diff_rules.items():
            setattr(self, name, self._differentiable(f, fprime))

    @staticmethod
    def _differentiable(f, fprime):
        """Decorator-style wrapper: lift a scalar math function into
        one that also propagates derivatives through Dual inputs."""
        def wrapped(x, *args):
            if isinstance(x, Dual):
                return Dual(f(x.real, *args), fprime(x.real) * x.dual)
            return f(x, *args)
        return wrapped

    def __getattr__(self, name):
        # Fallback for anything not in _diff_rules (e.g. math.pi, math.floor)
        return getattr(self._math, name)
dmath = EnhancedMath(_math)