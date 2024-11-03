import SkateBack

def test1():
    sk = SkateBack()
    sk.accelerate_to("L", 0.2)
    sk.accelerate_to("L", 0.6)
    sk.accelerate_to("R", 0.2)
    sk.accelerate_to("R", 0.6)