import utility
import io
from numpy.testing import assert_approx_equal

test_filepath = './test/test_audio2.wav'

def calculate_BPM_test():
    with open(test_filepath, 'rb') as f:
        test_bytes = io.BytesIO(f.read())

        assert_approx_equal(utility.calculateBPMFromBytes(test_bytes), 78.3, significant=3)

calculate_BPM_test()