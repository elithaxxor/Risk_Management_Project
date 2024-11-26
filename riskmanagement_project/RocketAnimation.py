import os
import time
from PIL import Image
import streamlit as st

class RocketAnimation:
    def __init__(self, roof=20):
        """
        Initialize the RocketAnimation class.
        :param roof: Initial height of the rocket (number of newlines before the rocket is displayed).
        """
        self.roof = roof

    def animate(self):
        """
        Animate the rocket descending and clear the console at each step.
        :return: A string message when the animation ends.
        """
        while True:
            print("\n" * self.roof)
            print("          /\        ")
            print("          ||        ")
            print("          ||        ")
            print("         /||\        ")
            time.sleep(0.2)
            os.system('clear')  # Use 'cls' if on Windows.
            self.roof -= 1
            if self.roof == 15:
                return "\nCopyleft Material, from Adel Al-Aali. All Wrongs Reserved.\n\n"

    def display_rocket_image(self, image_path):
        """
        Display a rocket-related image and additional text in Streamlit.
        :param image_path: Path to the image file.
        """
        try:
            image = Image.open(image_path)
            st.image(image, use_column_width=True)
            st.write('''
                #  Why *Invest* when you could **SPECULATE**!
                [Copyleft - All Wrongs Reserved](https://github.com/elithaxxor?tab=repositories)
                ***
            ''')
        except FileNotFoundError:
            print(f"Error: The image file '{image_path}' was not found.")
        except Exception as e:
            print(f"An error occurred while displaying the image: {e}")

    def run(self):

        ''' 1. Create an instance of the RocketAnimation class
            2. Animate the rocket
            3. Display the rocket image and additional text in Streamlit
        '''
        rocket = RocketAnimation(roof=20)
        message = rocket.animate()
        print(message * 3)

        # Display the rocket image and additional text in Streamlit
        # rocket.display_rocket_image("wsb.png")
def main():
    r = RocketAnimation()
    r.run()



# Example Usage
if __name__ == "__main__":
    main()
