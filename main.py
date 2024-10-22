'''
The main file for the LynnLib library.
Mainly used for testing in-development features.
'''

import lynn_lib

def main():
    '''Main function for the LynnLib library'''
    print(lynn_lib.styled("test", lynn_lib.COLORS.Foreground.RED))

if __name__ == "__main__":
    main()
