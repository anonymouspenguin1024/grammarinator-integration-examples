###### Test case
```javascript
{% if reduced %}
{{reduced}}
{% else %}
{{test}}
{% endif %}
```

{% if stderr %}
###### Output
```text
{{stderr|trim}}
```
{% endif %}
