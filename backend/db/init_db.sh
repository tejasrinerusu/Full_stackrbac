#!/usr/bin/env bash
alembic upgrade head
python seed_superuser.py admin@test.com 12345678
python seed_user.py manager@test.com 12345678
python seed_user.py senior@test.com 12345678
python seed_user.py test@test.com 12345678
python seed_permission.py setting.create setting.read setting.update setting.delete
