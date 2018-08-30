"""[summary]
Main module.
[description]
The main module starts the web service
"""
from app import app
if __name__ == "__main__":
    """[summary]
    [description]
    The main module defines exception handler and runs the web service
    """
    # app.debug = True
<<<<<<< HEAD
    app.run(host= '0.0.0.0',port=5003)
=======
    app.run(host= '0.0.0.0',port=5001)
>>>>>>> 5644cb4b55e39da905113968aab56182547ff1a5
