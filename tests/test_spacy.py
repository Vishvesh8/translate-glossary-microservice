#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pytest  # noqa

import spacy


def test_spacy_language_model():
    nlp = spacy.load('en_core_web_sm')
    assert callable(nlp)
    assert len(list(nlp("Hello world!"))) == 3
