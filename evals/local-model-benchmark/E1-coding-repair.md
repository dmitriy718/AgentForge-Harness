# E1 Coding Repair

You are reviewing this failing Python function:

```python
def has_sections(report):
    required = ["Evidence", "Risks", "Validation"]
    return required in report
```

The input is a Markdown string. Return only a corrected Python function that returns `True` when all three section headings are present and `False` otherwise.

