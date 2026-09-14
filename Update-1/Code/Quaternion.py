import numpy as np

class quaternion_ijk:
    def __init__(self,q0=0,q1=0,q2=0,q3=0):
        self.q0 = q0        # Scalar Part
        self.Q = {"i":q1,"j":q2,"k":q3} # Vector Part

    def disp(self):
        print(f"{self.q0} + {self.Q["i"]}i + {self.Q["j"]}j + {self.Q["k"]}k")

    def __str__(self):
        temp = []
        if self.q0!=0:
            temp = [str(round(self.q0,3))]
        for i in self.Q.keys():
            if abs(self.Q[i])>0.00001:
                temp.append(str(round(self.Q[i],3))+i)
        # return f"{self.q0} + {self.Q["i"]}i + {self.Q["j"]}j + {self.Q["k"]}k"
        return " + ".join(temp)

    @property
    def C(self):        # Conjugate
        return quaternion_ijk(self.q0,-self.Q["i"],-self.Q["j"],-self.Q["k"])
    
    @property
    def N(self):        # Norm
        ans = self.q0**2
        for i in self.Q.keys():
            ans += self.Q[i]**2
        return ans**0.5
    
    @property
    def I(self):        # Inverse
        norm = self.N**2
        return quaternion_ijk(self.q0/norm,-1*self.Q["i"]/norm,-1*self.Q["j"]/norm,-1*self.Q["k"]/norm)
    
    def __neg__(self):  # Negative
        return quaternion_ijk(-self.q0,-self.Q["i"],-self.Q["j"],-self.Q["k"])
    
    def __add__(self, y : quaternion_ijk) -> quaternion_ijk:
        sum = quaternion_ijk()
        sum.q0 = self.q0 + y.q0
        for i in sum.Q.keys():
            sum.Q[i] = self.Q[i]+y.Q[i]
        return sum
    
    def __sub__(self, y : quaternion_ijk) -> quaternion_ijk:
        sum = quaternion_ijk()
        sum.q0 = self.q0 - y.q0
        for i in sum.Q.keys():
            sum.Q[i] = self.Q[i]-y.Q[i]
        return sum
    
    def mul_support(self, i : str, j : str) -> str:
        temp = {0:"i",1:"j",2:"k"}
        i = ord(i)-ord("i")
        j = ord(j)-ord("i")
        if (i+1)%3==j:
            return 1,temp[(j+1)%3]
        return -1,temp[(i+1)%3]
    
    def __mul__(self, x):
        if isinstance(x, (int, float)):
            return quaternion_ijk(self.q0*x,self.Q["i"]*x,self.Q["j"]*x,self.Q["k"]*x)
        elif isinstance(x, (quaternion_ijk)):
            prod = quaternion_ijk()
            prod.q0 = self.q0 * x.q0
            for i in prod.Q.keys():
                prod.Q[i] += self.q0*x.Q[i]
                prod.Q[i] += x.q0*self.Q[i]
            for i in prod.Q.keys():
                for j in prod.Q.keys():
                    if i==j:
                        prod.q0 -= self.Q[i]*x.Q[j]
                    else:
                        sign, target = self.mul_support(i,j)
                        prod.Q[target] += sign*(self.Q[i]*x.Q[j])
            return prod
        raise NotImplementedError("Unsupported data type")

    def sandwich(self, theta : float) -> quaternion_ijk:
        ct = np.cos(np.deg2rad(theta/2))
        st = np.sin(np.deg2rad(theta/2))/(3**0.5)
        q = quaternion_ijk(ct,st,st,st)
        return q * self * q.C

    def sandwich_2(self, theta : float, n : list[float]) -> quaternion_ijk:
        ct = np.cos(np.deg2rad(theta/2))
        st = np.sin(np.deg2rad(theta/2))
        norm = (n[0]**2+n[1]**2+n[2]**2)**0.5
        n_new = [i/norm for i in n]
        q = quaternion_ijk(ct,n_new[0]*st,n_new[1]*st,n_new[2]*st)
        return q * self * q.C


def euler2quaternion(phi : float, theta : float, psi : float) -> quaternion_ijk:
    cx = np.cos(np.deg2rad(phi/2))
    cy = np.cos(np.deg2rad(theta/2))
    cz = np.cos(np.deg2rad(psi/2))
    sx = np.sin(np.deg2rad(phi/2))
    sy = np.sin(np.deg2rad(theta/2))
    sz = np.sin(np.deg2rad(psi/2))
    q0 = cz*cy*cx + sz*sy*sx
    q1 = cz*cy*sx - sz*sy*cx
    q2 = cz*sy*cx + sz*cy*sx
    q3 = sz*cy*cx - cz*sy*sx
    return quaternion_ijk(q0,q1,q2,q3)

def quaternion2euler(q : quaternion_ijk) -> list:
    q0 = q.q0
    q1 = q.Q["i"]
    q2 = q.Q["j"]
    q3 = q.Q["k"]
    theta = np.arcsin(2*(q0*q2-q1*q3))
    phi = np.arctan2((2*(q2*q3+q0*q1)),(1-2*(q1**2+q2**2)))
    psi = np.arctan2((2*(q1*q2+q0*q3)),(1-2*(q2**2+q3**2)))
    return [round(float(np.rad2deg(phi)),3),round(float(np.rad2deg(theta)),3),round(float(np.rad2deg(psi)),3)]

        