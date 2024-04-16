# Oak
# Turing

Turing Machine Synthesis based on a SAT solver

![Screenshot of unary single bit-shift being synthesized](Turing/Screenshots/Final_View.jpg)



**Status:** Complete. Capable of live Turing machine synthesis. Note: this is a research tool, and a precursor to a more complete system which operates on a different language. The theory document is a very rough draft and riddled with holes, and the GUI does not support all features allowed for my the theory and supported by the engine. Notably missing are the ability to live and dynamically add or remove examples, adjust example sizes, and change the number of states.



**Setup:** 

1. If your python does not come with these already installed, run `sudo yum install python-devel python3-tkinter python3-pillow-tk` or your package manager's equivalent
2. `$pip install pillow`
3. `$pip install pycosat`
4. `$cd Turing/Program`
5. `$python3 main.py`
