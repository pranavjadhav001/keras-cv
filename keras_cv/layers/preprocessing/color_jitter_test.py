# Copyright 2022 The KerasCV Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import numpy as np
import tensorflow as tf
from keras_cv.layers.preprocessing.color_jitter import ColorJitter


class ColorJitterTest(tf.test.TestCase):
    # Test 1: Check input and output shape. It should match.
    def test_return_shapes(self):
        batch_input = tf.ones((2, 512, 512, 3))
        non_square_batch_input = tf.ones((2, 1024, 512, 3))
        unbatch_input = tf.ones((512, 512, 3))

        layer = ColorJitter()
        batch_output = layer(batch_input, training=True)
        non_square_batch_output = layer(non_square_batch_input, training=True)
        unbatch_output = layer(unbatch_input, training=True)

        self.assertEqual(batch_output.shape, [2, 512, 512, 3])
        self.assertEqual(non_square_batch_output.shape, [2, 1024, 512, 3])
        self.assertEqual(unbatch_output.shape, [512, 512, 3])

    # Test 2: Check if the factor ranges are set properly.
    def test_factor_range(self):
        layer = ColorJitter(
            brightness_factor=0.5,
            contrast_factor=(0.5, 0.9),
            saturation_factor=(0.5, 0.9),
            hue_factor=0.5,
        )

        self.assertEqual(layer.brightness_factor, 0.5)
        self.assertEqual(layer.contrast_factor, [0.5, 0.9])
        self.assertEqual(layer.saturation_factor, [0.5, 0.9])
        self.assertEqual(layer.hue_factor, 0.5)

    # Test 3: Test if it is OK to run on graph mode.
    def test_in_tf_function(self):
        inputs = tf.ones((2, 512, 512, 3))

        layer = ColorJitter(
            brightness_factor=0.5,
            contrast_factor=(0.5, 0.9),
            saturation_factor=(0.5, 0.9),
            hue_factor=0.5,
        )

        @tf.function
        def augment(x):
            return layer(x, training=True)

        outputs = augment(inputs)
        self.assertNotAllClose(inputs, outputs)

    # Test 4: Check if input and output dtype are same. It should match.
    def test_dtype(self):
        layer = ColorJitter(
            brightness_factor=0.1,
            contrast_factor=0.5,
            saturation_factor=0.9,
            hue_factor=0.1,
        )
        inputs = np.random.randint(0, 255, size=(224, 224, 3))

        print('a ', inputs.dtype)

        output = layer(inputs, training=True)
        print('b ', output.dtype)
        self.assertEqual(output.dtype, inputs.dtype)

        inputs = tf.cast(inputs, tf.float32)
        output = layer(inputs, training=True)
        self.assertEqual(output.dtype, inputs.dtype)

    # Test 5: Check if get_config and from_config work as expected.
    def test_config(self):
        layer = ColorJitter(
            brightness_factor=0.5,
            contrast_factor=(0.5, 0.9),
            saturation_factor=(0.5, 0.9),
            hue_factor=0.5,
            seed=1,
        )

        config = layer.get_config()
        self.assertEqual(config["brightness_factor"], 0.5)
        self.assertEqual(config["contrast_factor"], [0.5, 0.9])
        self.assertEqual(config["saturation_factor"], [0.5, 0.9])
        self.assertEqual(config["hue_factor"], 0.5)
        self.assertEqual(config["seed"], 1)

        reconstructed_layer = ColorJitter.from_config(config)
        self.assertEqual(reconstructed_layer.brightness_factor, layer.brightness_factor)
        self.assertEqual(reconstructed_layer.contrast_factor, layer.contrast_factor)
        self.assertEqual(reconstructed_layer.saturation_factor, layer.saturation_factor)
        self.assertEqual(reconstructed_layer.hue_factor, layer.hue_factor)
        self.assertEqual(reconstructed_layer.seed, layer.seed)

    # Test 6: Check if inference model is OK.
    def test_inference(self):
        layer = ColorJitter()
        inputs = np.random.randint(0, 255, size=(224, 224, 3))
        output = layer(inputs, training=False)
        self.assertAllClose(inputs, output)
