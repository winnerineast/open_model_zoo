"""
Copyright (c) 2019 Intel Corporation

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from ..config import NumberField, PathField
from ..representation import DetectionAnnotation
from ..utils import convert_bboxes_xywh_to_x1y1x2y2, read_txt

from .format_converter import BaseFormatConverter


class WiderFormatConverter(BaseFormatConverter):
    __provider__ = 'wider'
    annotation_types = (DetectionAnnotation, )

    @classmethod
    def parameters(cls):
        parameters = super().parameters()
        parameters.update({
            'annotation_file': PathField(
                description="Path to xml file, which contains ground truth data in WiderFace dataset format."
            ),
            'label_start': NumberField(
                value_type=int, optional=True, default=1,
                description="Specifies face label index in label map. Default value is 1. "
                            "You can provide another value, if you want to use this"
            )
        })

        return parameters

    def configure(self):
        self.annotation_file = self.get_value_from_config('annotation_file')
        self.label_start = self.get_value_from_config('label_start')

    def convert(self):
        image_annotations = read_txt(self.annotation_file)
        image_ids = []
        for image_id, line in enumerate(image_annotations):
            if '.jpg' in line:
                image_ids.append(image_id)

        annotations = []
        for image_id in image_ids:
            identifier = image_annotations[image_id]
            bbox_count = image_annotations[image_id + 1]
            bbox_lines = image_annotations[image_id + 2:image_id + 2 + int(bbox_count)]

            x_mins, y_mins, x_maxs, y_maxs = [], [], [], []
            for bbox in bbox_lines:
                x_min, y_min, x_max, y_max = convert_bboxes_xywh_to_x1y1x2y2(*(map(float, (bbox.split(' ')[0:4]))))
                x_mins.append(x_min)
                y_mins.append(y_min)
                x_maxs.append(x_max)
                y_maxs.append(y_max)

            annotations.append(DetectionAnnotation(
                identifier, [self.label_start] * len(x_mins),
                x_mins, y_mins, x_maxs, y_maxs
            ))

        return annotations, {'label_map': {0: '__background__', self.label_start: 'face'}, 'background_label': 0}
