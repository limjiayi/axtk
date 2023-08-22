from dataclasses import dataclass
from typing import Optional
from axtk.common.spans import Span



ANNOTATION_SCHEMES = {
    'IOB1',
    'IOB2',
    'BILOU',
    'IOBES',
}

SCHEME_SYNONYMS = {
    'IOB': 'IOB1',
    'BILUO': 'BILOU',
    'BIOES': 'IOBES',
}



@dataclass(frozen=True, order=True)
class TokenSpan(Span):
    label: Optional[str]



def normalize_scheme(scheme: str) -> str:
    scheme_upper = scheme.upper()
    scheme_upper = SCHEME_SYNONYMS.get(scheme_upper, scheme_upper)
    if scheme_upper not in ANNOTATION_SCHEMES:
        raise ValueError(f'invalid {scheme=}')
    return scheme_upper



def is_valid_label(label: str, scheme: str) -> bool:
    scheme = normalize_scheme(scheme)
    if scheme == 'IOB1':
        return iob_valid_label(label)
    elif scheme == 'IOB2':
        return iob2_valid_label(label)
    elif scheme == 'BILOU':
        return biluo_valid_label(label)
    elif scheme == 'IOBES':
        return iobes_valid_label(label)
    else:
        raise ValueError(f'invalid {scheme=}')



def is_valid_transition(from_label: Optional[str], to_label: Optional[str], scheme: str) -> bool:
    scheme = normalize_scheme(scheme)
    if scheme == 'IOB1':
        return iob_valid_transition(from_label, to_label)
    elif scheme == 'IOB2':
        return iob2_valid_transition(from_label, to_label)
    elif scheme == 'BILOU':
        return biluo_valid_transition(from_label, to_label)
    elif scheme == 'IOBES':
        return iobes_valid_transition(from_label, to_label)
    else:
        raise ValueError(f'invalid {scheme=}')



def load_spans(labels: list[str], scheme: str) -> list[TokenSpan]:
    scheme = normalize_scheme(scheme)
    if scheme == 'IOB1':
        return iob_to_spans(labels)
    elif scheme == 'IOB2':
        return iob2_to_spans(labels)
    elif scheme == 'BILOU':
        return biluo_to_spans(labels)
    elif scheme == 'IOBES':
        return iobes_to_spans(labels)
    else:
        raise ValueError(f'invalid {scheme=}')



def dump_spans(num_tokens: int, spans: list[TokenSpan], scheme: str) -> list[str]:
    scheme = normalize_scheme(scheme)
    if scheme == 'IOB1':
        return spans_to_iob(num_tokens, spans)
    elif scheme == 'IOB2':
        return spans_to_iob2(num_tokens, spans)
    elif scheme == 'BILOU':
        return spans_to_biluo(num_tokens, spans)
    elif scheme == 'IOBES':
        return spans_to_iobes(num_tokens, spans)
    else:
        raise ValueError(f'invalid {scheme=}')



def convert_labels(labels: list[str], from_scheme: str, to_scheme: str) -> list[str]:
    return dump_spans(len(labels), load_spans(labels, from_scheme), to_scheme)



def parse_label(label: str, sep: str = '-') -> tuple[Optional[str], Optional[str]]:
    if sep in label:
        return tuple(label.split(sep=sep, maxsplit=1))
    elif label in {'O', 'B', 'I', 'L', 'U', 'E', 'S'}:
        return label, None
    else:
        return None, label



def iob_valid_label(label: str) -> bool:
    return label and label[0] in {'B', 'I', 'O'}

def iob2_valid_label(label: str) -> bool:
    return label and label[0] in {'B', 'I', 'O'}

def biluo_valid_label(label: str) -> bool:
    return label and label[0] in {'B', 'I', 'L', 'U', 'O'}

def iobes_valid_label(label: str) -> bool:
    return label and label[0] in {'B', 'I', 'E', 'S', 'O'}



def iob_valid_transition(from_label: Optional[str], to_label: Optional[str]) -> bool:
    if from_label is None:
        return to_label is not None and to_label[0] in {'I', 'O'}
    if to_label is None:
        return True
    from_tag, from_entity = parse_label(from_label)
    to_tag, to_entity = parse_label(to_label)
    if from_tag == 'O' and to_tag in {'O', 'I'}:
        return True
    if from_tag == 'B' and to_tag == 'I':
        return from_entity == to_entity
    if from_tag == 'B' and to_tag in {'O', 'B'}:
        return True
    if from_tag == 'I' and to_tag == 'I':
        return from_entity == to_entity
    if from_tag == 'I' and to_tag in {'O', 'B'}:
        return True
    return False

def iob2_valid_transition(from_label: Optional[str], to_label: Optional[str]) -> bool:
    if from_label is None:
        return to_label is not None and to_label[0] in {'B', 'O'}
    if to_label is None:
        return True
    from_tag, from_entity = parse_label(from_label)
    to_tag, to_entity = parse_label(to_label)
    if from_tag == 'O' and to_tag in {'O', 'B'}:
        return True
    if from_tag == 'B' and to_tag == 'I':
        return from_entity == to_entity
    if from_tag == 'B' and to_tag in {'O', 'B'}:
        return True
    if from_tag == 'I' and to_tag == 'I':
        return from_entity == to_entity
    if from_tag == 'I' and to_tag in {'O', 'B'}:
        return True
    return False

def biluo_valid_transition(from_label: Optional[str], to_label: Optional[str]) -> bool:
    if from_label is None:
        return to_label is not None and to_label[0] in {'B', 'U', 'O'}
    from_tag, from_entity = parse_label(from_label)
    if to_label is None:
        return from_tag in {'L', 'U', 'O'}
    to_tag, to_entity = parse_label(to_label)
    if from_tag == 'O' and to_tag in {'O', 'B', 'U'}:
        return True
    if from_tag == 'B' and to_tag in {'I', 'L'}:
        return from_entity == to_entity
    if from_tag == 'I' and to_tag in {'I', 'L'}:
        return from_entity == to_entity
    if from_tag == 'L' and to_tag in {'O', 'B', 'U'}:
        return True
    if from_tag == 'U' and to_tag in {'O', 'B', 'U'}:
        return True
    return False

def iobes_valid_transition(from_label: Optional[str], to_label: Optional[str]) -> bool:
    if from_label is None:
        return to_label is not None and to_label[0] in {'B', 'S', 'O'}
    from_tag, from_entity = parse_label(from_label)
    if to_label is None:
        return from_tag in {'E', 'U', 'O'}
    to_tag, to_entity = parse_label(to_label)
    if from_tag == 'O' and to_tag in {'O', 'B', 'S'}:
        return True
    if from_tag == 'B' and to_tag in {'I', 'E'}:
        return from_entity == to_entity
    if from_tag == 'I' and to_tag in {'I', 'E'}:
        return from_entity == to_entity
    if from_tag == 'E' and to_tag in {'O', 'B', 'S'}:
        return True
    if from_tag == 'S' and to_tag in {'O', 'B', 'S'}:
        return True
    return False



def iob_to_spans(labels: list[str]) -> list[TokenSpan]:
    spans = []
    start = span_entity = None
    previous_label = None
    for i, label in enumerate(labels):
        if not iob_valid_label(label):
            raise ValueError(f'invalid {label=}')
        if not iob_valid_transition(previous_label, label):
            prev = 'START' if previous_label is None else previous_label
            raise ValueError(f'invalid transition {prev!r} -> {label!r}')
        tag, entity = parse_label(label)
        if tag == 'O':
            if start is not None:
                spans.append(TokenSpan(start, i, span_entity))
                start = span_entity = None
        elif tag == 'B':
            if start is not None:
                spans.append(TokenSpan(start, i, span_entity))
            start = i
            span_entity = entity
        elif tag == 'I':
            if start is None:
                start = i
                span_entity = entity
        previous_label = label
    if start is not None:
        spans.append(TokenSpan(start, len(labels), span_entity))
    return spans

def iob2_to_spans(labels: list[str]) -> list[TokenSpan]:
    spans = []
    start = span_entity = None
    previous_label = None
    for i, label in enumerate(labels):
        if not iob2_valid_label(label):
            raise ValueError(f'invalid {label=}')
        if not iob2_valid_transition(previous_label, label):
            prev = 'START' if previous_label is None else previous_label
            raise ValueError(f'invalid transition {prev!r} -> {label!r}')
        tag, entity = parse_label(label)
        if tag == 'O':
            if start is not None:
                spans.append(TokenSpan(start, i, span_entity))
                start = span_entity = None
        elif tag == 'B':
            if start is not None:
                spans.append(TokenSpan(start, i, span_entity))
            start = i
            span_entity = entity
        previous_label = label
    if start is not None:
        spans.append(TokenSpan(start, len(labels), span_entity))
    return spans

def biluo_to_spans(labels: list[str]) -> list[TokenSpan]:
    spans = []
    start = span_entity = None
    previous_label = None
    for i, label in enumerate(labels):
        if not biluo_valid_label(label):
            raise ValueError(f'invalid {label=}')
        if not biluo_valid_transition(previous_label, label):
            prev = 'START' if previous_label is None else previous_label
            raise ValueError(f'invalid transition {prev!r} -> {label!r}')
        tag, entity = parse_label(label)
        if tag == 'O':
            if start is not None:
                spans.append(TokenSpan(start, i, span_entity))
                start = span_entity = None
        elif tag == 'B':
            start = i
            span_entity = entity
        elif tag == 'L':
            spans.append(TokenSpan(start, i, span_entity))
            start = span_entity = None
        elif tag == 'U':
            spans.append(TokenSpan(i, i+1, span_entity))
        previous_label = label
    if not biluo_valid_transition(labels[-1], None):
        raise ValueError(f'invalid transition {label!r} -> END')
    if start is not None:
        spans.append(TokenSpan(start, len(labels), span_entity))
    return spans

def iobes_to_spans(labels: list[str]) -> list[TokenSpan]:
    spans = []
    start = span_entity = None
    previous_label = None
    for i, label in enumerate(labels):
        if not iobes_valid_label(label):
            raise ValueError(f'invalid {label=}')
        if not iobes_valid_transition(previous_label, label):
            prev = 'START' if previous_label is None else previous_label
            raise ValueError(f'invalid transition {prev!r} -> {label!r}')
        tag, entity = parse_label(label)
        if tag == 'O':
            if start is not None:
                spans.append(TokenSpan(start, i, span_entity))
                start = span_entity = None
        elif tag == 'B':
            start = i
            span_entity = entity
        elif tag == 'E':
            spans.append(TokenSpan(start, i, span_entity))
            start = span_entity = None
        elif tag == 'S':
            spans.append(TokenSpan(i, i+1, span_entity))
        previous_label = label
    if not iobes_valid_transition(labels[-1], None):
        raise ValueError(f'invalid transition {label!r} -> END')
    if start is not None:
        spans.append(TokenSpan(start, len(labels), span_entity))
    return spans



def spans_to_iob(num_tokens: int, spans: list[TokenSpan]) -> list[str]:
    if Span.any_overlap(spans):
        raise ValueError('overlapping spans')
    labels = ['O'] * num_tokens
    for span in spans:
        for i in span.range():
            if i == span.first and i > 0 and labels[i-1] != 'O':
                label = f'B-{span.label}' if span.label else 'B'
            else:
                label = f'I-{span.label}' if span.label else 'I'
            labels[i] = label
    return labels

def spans_to_iob2(num_tokens: int, spans: list[TokenSpan]) -> list[str]:
    if Span.any_overlap(spans):
        raise ValueError('overlapping spans')
    labels = ['O'] * num_tokens
    for span in spans:
        for i in span.range():
            if i == span.first:
                label = f'B-{span.label}' if span.label else 'B'
            else:
                label = f'I-{span.label}' if span.label else 'I'
            labels[i] = label
    return labels

def spans_to_biluo(num_tokens: int, spans: list[TokenSpan]) -> list[str]:
    if Span.any_overlap(spans):
        raise ValueError('overlapping spans')
    labels = ['O'] * num_tokens
    for span in spans:
        for i in span.range():
            if span.length() == 1:
                label = f'U-{span.label}' if span.label else 'U'
            elif i == span.first:
                label = f'B-{span.label}' if span.label else 'B'
            elif i == span.last:
                label = f'L-{span.label}' if span.label else 'L'
            else:
                label = f'I-{span.label}' if span.label else 'I'
            labels[i] = label
    return labels

def spans_to_iobes(num_tokens: int, spans: list[TokenSpan]) -> list[str]:
    if Span.any_overlap(spans):
        raise ValueError('overlapping spans')
    labels = ['O'] * num_tokens
    for span in spans:
        for i in span.range():
            if span.length() == 1:
                label = f'S-{span.label}' if span.label else 'S'
            elif i == span.first:
                label = f'B-{span.label}' if span.label else 'B'
            elif i == span.last:
                label = f'E-{span.label}' if span.label else 'E'
            else:
                label = f'I-{span.label}' if span.label else 'I'
            labels[i] = label
    return labels



def iob_to_iob2(labels: list[str]) -> list[str]:
    return spans_to_iob2(len(labels), iob_to_spans(labels))

def iob_to_biluo(labels: list[str]) -> list[str]:
    return spans_to_biluo(len(labels), iob_to_spans(labels))

def iob_to_iobes(labels: list[str]) -> list[str]:
    return spans_to_iobes(len(labels), iob_to_spans(labels))

def iob2_to_iob(labels: list[str]) -> list[str]:
    return spans_to_iob(len(labels), iob2_to_spans(labels))

def iob2_to_biluo(labels: list[str]) -> list[str]:
    return spans_to_biluo(len(labels), iob2_to_spans(labels))

def iob2_to_iobes(labels: list[str]) -> list[str]:
    return spans_to_iobes(len(labels), iob2_to_spans(labels))

def biluo_to_iob(labels: list[str]) -> list[str]:
    return spans_to_iob(len(labels), biluo_to_spans(labels))

def biluo_to_iob2(labels: list[str]) -> list[str]:
    return spans_to_iob2(len(labels), biluo_to_spans(labels))

def biluo_to_iobes(labels: list[str]) -> list[str]:
    return spans_to_iobes(len(labels), biluo_to_spans(labels))

def iobes_to_iob(labels: list[str]) -> list[str]:
    return spans_to_iob(len(labels), iobes_to_spans(labels))

def iobes_to_iob2(labels: list[str]) -> list[str]:
    return spans_to_iob2(len(labels), iobes_to_spans(labels))

def iobes_to_biluo(labels: list[str]) -> list[str]:
    return spans_to_biluo(len(labels), iobes_to_spans(labels))
