from __future__ import print_function

import torch

from .helpers.utils import BaseTest, assertTensorAlmostEqual
from .helpers.basic_models import ReLULinearDeepLiftModel

from captum.attr._core.neuron_deep_lift import NeuronDeepLift, NeuronDeepLiftShap
from .test_layer_deeplift_basic import (
    _create_inps_and_base_for_deeplift_neuron_layer_testing,
    _create_inps_and_base_for_deepliftshap_neuron_layer_testing,
)


class Test(BaseTest):
    def test_relu_neuron_deeplift(self):
        model = ReLULinearDeepLiftModel()

        x1 = torch.tensor([[-10.0, 1.0, -5.0]], requires_grad=True)
        x2 = torch.tensor([[3.0, 3.0, 1.0]], requires_grad=True)

        inputs = (x1, x2)

        neuron_dl = NeuronDeepLift(model, model.relu)
        attributions = neuron_dl.attribute(inputs, 0, attribute_to_neuron_input=True)
        assertTensorAlmostEqual(self, attributions[0], [[-30.0, 1.0, -0.0]])
        assertTensorAlmostEqual(self, attributions[1], [[0.0, 0.0, 0.0]])

        attributions = neuron_dl.attribute(inputs, 0, attribute_to_neuron_input=False)
        assertTensorAlmostEqual(self, attributions[0], [[0.0, 0.0, 0.0]])
        assertTensorAlmostEqual(self, attributions[1], [[0.0, 0.0, 0.0]])

    def test_linear_neuron_deeplift(self):
        model = ReLULinearDeepLiftModel()
        inputs, baselines = _create_inps_and_base_for_deeplift_neuron_layer_testing()

        neuron_dl = NeuronDeepLift(model, model.l3)
        attributions = neuron_dl.attribute(
            inputs, 0, baselines, attribute_to_neuron_input=True
        )
        assertTensorAlmostEqual(self, attributions[0], [[-0.0, 0.0, -0.0]])
        assertTensorAlmostEqual(self, attributions[1], [[0.0, 0.0, 0.0]])

        attributions = neuron_dl.attribute(
            inputs, 0, baselines, attribute_to_neuron_input=False
        )

        assertTensorAlmostEqual(self, attributions[0], [[-0.0, 0.0, -0.0]])
        assertTensorAlmostEqual(self, attributions[1], [[6.0, 9.0, 0.0]])

    def test_relu_deeplift_with_custom_attr_func(self):
        model = ReLULinearDeepLiftModel()
        inputs, baselines = _create_inps_and_base_for_deeplift_neuron_layer_testing()
        neuron_dl = NeuronDeepLift(model, model.l3)
        expected = ([0.0, 0.0, 0.0], [0.0, 0.0, 0.0])
        self._relu_custom_attr_func_assert(neuron_dl, inputs, baselines, expected)

    def test_relu_neuron_deeplift_shap(self):
        model = ReLULinearDeepLiftModel()
        (
            inputs,
            baselines,
        ) = _create_inps_and_base_for_deepliftshap_neuron_layer_testing()

        neuron_dl = NeuronDeepLiftShap(model, model.relu)
        attributions = neuron_dl.attribute(
            inputs, 0, baselines, attribute_to_neuron_input=True
        )
        assertTensorAlmostEqual(self, attributions[0], [[-30.0, 1.0, -0.0]])
        assertTensorAlmostEqual(self, attributions[1], [[0.0, 0.0, 0.0]])

        attributions = neuron_dl.attribute(
            inputs, 0, baselines, attribute_to_neuron_input=False
        )
        assertTensorAlmostEqual(self, attributions[0], [[0.0, 0.0, 0.0]])
        assertTensorAlmostEqual(self, attributions[1], [[0.0, 0.0, 0.0]])

    def test_linear_neuron_deeplift_shap(self):
        model = ReLULinearDeepLiftModel()
        (
            inputs,
            baselines,
        ) = _create_inps_and_base_for_deepliftshap_neuron_layer_testing()

        neuron_dl = NeuronDeepLiftShap(model, model.l3)
        attributions = neuron_dl.attribute(
            inputs, 0, baselines, attribute_to_neuron_input=True
        )
        assertTensorAlmostEqual(self, attributions[0], [[-0.0, 0.0, -0.0]])
        assertTensorAlmostEqual(self, attributions[1], [[0.0, 0.0, 0.0]])

        attributions = neuron_dl.attribute(
            inputs, 0, baselines, attribute_to_neuron_input=False
        )

        assertTensorAlmostEqual(self, attributions[0], [[-0.0, 0.0, -0.0]])
        assertTensorAlmostEqual(self, attributions[1], [[6.0, 9.0, 0.0]])

    def test_relu_deepliftshap_with_custom_attr_func(self):
        model = ReLULinearDeepLiftModel()
        (
            inputs,
            baselines,
        ) = _create_inps_and_base_for_deepliftshap_neuron_layer_testing()
        neuron_dl = NeuronDeepLiftShap(model, model.l3)
        expected = (torch.zeros(3, 3), torch.zeros(3, 3))
        self._relu_custom_attr_func_assert(neuron_dl, inputs, baselines, expected)

    def _relu_custom_attr_func_assert(self, attr_method, inputs, baselines, expected):
        def custom_attr_func(multipliers, inputs, baselines):
            return tuple(multiplier * 0.0 for multiplier in multipliers)

        attr = attr_method.attribute(
            inputs, 0, baselines, custom_attribution_func=custom_attr_func
        )
        assertTensorAlmostEqual(self, attr[0], expected[0], 0.0)
        assertTensorAlmostEqual(self, attr[1], expected[1], 0.0)