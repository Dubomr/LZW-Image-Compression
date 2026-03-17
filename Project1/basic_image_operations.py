from PIL import Image  # Image module from the Python Imaging Library
import numpy as np  # a fundamental package for scientific computing with Python
import os  # the os module is used for file and directory operations

# A function that reads then returns an image from a file with a given path.
def read_image_file(img_file_path):
   img = Image.open(img_file_path)
   return img

# A function that writes a given image to a file with a given path.
def write_image_file(img, img_file_path):
   img.save(img_file_path)

# A function that converts a color image to grayscale and returns the result.
def color_image_to_grayscale(img):
   img_gray = img.convert('L')
   return img_gray

# A function that converts a given image to a numpy array and returns the array.
def image_to_numpy_array(img):
   img_array = np.array(img)
   return img_array

# A function that converts a given numpy array to an image and returns the image.
def numpy_array_to_image(img_array):
   # converting the image array to uint8 (8-bit unsigned integer format) so that
   # pixel values are represented in the range [0, 255] to create a valid image
   img = Image.fromarray(np.uint8(img_array))
   return img

# A function that flattens a given numpy image array into a one-dimensional numpy
# array and returns the result.
def flatten_numpy_array(img_array):
   return img_array.flatten()

# A function that takes a one-dimensional sequence of pixel values, converts it
# to a numpy array of dtype uint8, reshapes it to the given image shape (height,
# width, channels) to obtain the image array, and returns the result.
def reshape_to_image_array(sequence_of_pixels, img_shape):
   if len(sequence_of_pixels) != np.prod(img_shape):
      raise ValueError('Pixel count does not match image shape.')
   pixel_array = np.array(sequence_of_pixels, dtype=np.uint8)
   img_array = pixel_array.reshape(img_shape)
   return img_array

if __name__ == "__main__":
   # get the current directory where this program is placed
   current_directory = os.path.dirname(os.path.realpath(__file__))

   # read a color (RGB) image from a file and display it
   input_file_path = os.path.join(current_directory, 'thumbs_up.bmp')
   color_image = read_image_file(input_file_path)
   color_image.show()

   # convert the color image to grayscale and display it
   grayscale_image = color_image_to_grayscale(color_image)
   grayscale_image.show()

   # write the grayscale image to a file
   output_file_path = os.path.join(current_directory, 'thumbs_up_grayscale.bmp')
   write_image_file(grayscale_image, output_file_path)

   # convert the grayscale image to a numpy array
   grayscale_image_array = image_to_numpy_array(grayscale_image)
   # print the shape of the array (height and width)
   print('Array shape (grayscale):', grayscale_image_array.shape)

   # convert the color image to a numpy array
   color_image_array = image_to_numpy_array(color_image)
   # print the shape of the array (height, width and number of channels)
   print('Array shape (RGB):', color_image_array.shape)

   # flatten the color image array to obtain a one-dimensional numpy array
   flat_pixels = flatten_numpy_array(color_image_array)
   # print the shape of the array (total number of pixels in all channels)
   print('Flat array shape (RGB):', flat_pixels.shape)

   # reshape the flat array to obtain another color image array
   color_image_array2 = reshape_to_image_array(flat_pixels, color_image_array.shape)
   # convert the array to a PIL image and display it
   color_image2 = numpy_array_to_image(color_image_array2)
   color_image2.show()

   # print whether two color image arrays are equal or not
   print(np.array_equal(color_image_array, color_image_array2))
