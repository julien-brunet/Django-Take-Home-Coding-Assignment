# Django-Take-Home-Coding-Assignment
A Django project modelling products, categories, and tags for an electrical
construction supply catalog, with a search-and-filter page built on Django
querysets.

Sample data is drawn from the electrical trade (wire, conduit, enclosures,
fittings, devices) so that filter combinations reflect realistic product
relationships.

## Requirements

- Python 3.13 (developed on 3.13.12)
- Django 6.0.7 (pinned in `requirements.txt`)
- SQLite (bundled with Python; no separate database server needed)

## Setup

```
git clone https://github.com/julien-brunet/Django-Take-Home-Coding-Assignment.git

cd Django-Take-Home-Coding-Assignment

cd product-catalog

python -m venv .venv

# macOS / Linux
source .venv/bin/activate

# Windows (Command Prompt)
.venv\Scripts\activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt

python manage.py migrate

python manage.py loaddata sample_data

python manage.py createsuperuser

python manage.py runserver
```

Then open:

- <http://127.0.0.1:8000/> — the product search and filter page
- <http://127.0.0.1:8000/admin/> — the Django admin

### Sample data

The database was populated through the Django admin interface as specified in
the assignment, then exported to a fixture so it can be reloaded in one command:

```bash
python manage.py loaddata sample_data
```

The fixture (`catalog/fixtures/sample_data.json`) contains 5 categories,
10 tags, and 20 products. The SQLite database file itself is intentionally
not committed.

To regenerate the fixture after changing data through the admin:

```bash
python manage.py dumpdata catalog --indent 2 > catalog/fixtures/sample_data.json
```

### Environment variables

The project runs with working defaults and needs no configuration. Two optional
variables are read from the environment if present:

| Variable             | Default                  | Purpose                     |
| -------------------- | ------------------------ | --------------------------- |
| `DJANGO_SECRET_KEY`  | insecure development key | Overrides the fallback key  |
| `DJANGO_DEBUG`       | `1`                      | Set to `0` to disable debug |

See `.env.example`. These exist to keep secrets out of source control; the
settings module is otherwise unchanged from the Django default.

## Data model

```
Category ──1:M──> Product <──M:M──> Tag
```

| Model      | Fields                                   |
| ---------- | -----------------------------------------|
| `Category` | `name`, `slug`                           |
| `Tag`      | `name`, `slug`                           |
| `Product`  | `name`, `description`, `category`, `tags`|

### Design decisions

**`Product.category` uses `on_delete=SET_NULL` with `null=True`.**
Deleting a category should not delete the products in it. Products whose
category is removed become uncategorised rather than disappearing. 
The template renders a null category as "Uncategorized".

**Tags use a plain `ManyToManyField`, not a `through` model.** The relationship
carries no data of its own, so an explicit intermediary would add indirection
without adding capability.

**Slugs on `Category` and `Tag`.** Filters are expressed as
`?category=wire-cable` rather than `?category=3`, which keeps URLs readable and
decouples them from primary keys.

**No custom database indexes.** The description search uses `icontains`, which
performs a full scan regardless of indexing. At this data volume none is warranted. A
production version would use full-text search (PostgreSQL `SearchVector` or an
external index) rather than `icontains`.

## Search and filter implementation

All filtering happens in a single view, `catalog.views.product_list`.

| Parameter  | Behaviour                                                  |
| ---------- | -----------------------------------------------------------|
| `q`        | Case-insensitive match across product name and description |
| `category` | Category slug                                              |
| `tags`     | Tag slug; repeatable (`?tags=copper&tags=pvc`)             |
| `tag_mode` | `all` (default, AND) or `any` (OR)                         |


### Query efficiency

`select_related("category")` resolves the foreign key in the same query via a
join; `prefetch_related("tags")` fetches all tags in one additional query. The
template accesses `product.tags.all`, which reads from the prefetch cache.
Without both, rendering 20 products with their categories and tags issues
roughly 41 queries. The same treatment is applied to the admin
changelist via `list_select_related` and a `get_queryset` override.

## Front end

A single Django template, `catalog/templates/catalog/product_list.html`. No
front-end framework and no build step.

The form submits with `GET` rather than `POST`, so filter state lives in the
URL: results are bookmarkable and shareable, refreshing does not prompt a
resubmit, and the view can be exercised directly from the address bar. Selected
values are re-rendered into the form so filters persist visibly across
submissions.

Styling is intentionally minimal, per the assignment note that design is not
being assessed.

## Assumptions

- A product belongs to at most one category and may carry any number of tags,
  including none.
- Search covers product name in addition to description. Description alone was
  required; including the name matches what a user of a parts catalog would
  expect when typing a product name.
- Search terms are treated as a single substring, not as independent keywords.
- Tags are intentionally orthogonal to categories — `Copper` spans wire, lugs,
  and ground bars.
- Empty or whitespace-only parameters are ignored rather than treated as
  filters that match nothing.
- Results are ordered by name (`Meta.ordering`); no relevance ranking.

## AI usage

No AI was used in the creation of this project with the exception of README.md documentation. 

## Possible extensions

Deliberately out of scope for this exercise, but the next things I would add:

- Full-text search with ranking, replacing `icontains`
- Pagination (unnecessary at 20 products, needed at scale)
- Tag facet counts showing how many results each tag would yield

## Project structure

```
product-catalog/
├── config/                     # Project settings and root URLconf
├── catalog/
│   ├── models.py               # Category, Tag, Product
│   ├── views.py                # product_list: search and filter logic
│   ├── admin.py                # Admin registration
│   ├── urls.py
│   ├── fixtures/
│   │   └── sample_data.json    # 5 categories, 10 tags, 20 products
│   ├── migrations/
│   └── templates/catalog/
│       └── product_list.html
├── manage.py
├── requirements.txt
└── README.md
```