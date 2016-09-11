""" Metainf block field registrations.

The META_FIELDS dictionary registers allowable fields in the markdown
metainf block as well as the type and default value.

The dictionary structure is defined as
```
META_FIELDS = {
    'camel_cased_field_name': ('python_type', default_value)
}
```

"""
META_FIELDS = {
    'title': ('unicode', None),
    'nav_name': ('unicode', None),
    'description': ('unicode', None),
    'author': ('unicode', None),
    'date': ('unicode', None),
    'order': ('int', 0),
    'template': ('unicode', None),
    'teaser': ('unicode', None),
    'teaser_image': ('unicode', None),
    'sitemap_priority': ('unicode', None),
    'sitemap_changefreq': ('unicode', None),
}
