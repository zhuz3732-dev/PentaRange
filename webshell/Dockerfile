# Apache + mod_php. This is the service that actually executes what the upload challenges produce.
# It exists because "the file landed on disk" is not an exploit: .htaccess only means something to
# a server that honours it, and a webshell only means something to a server that runs it.
FROM php:8.2-apache

RUN a2enmod php8 rewrite headers \
 && sed -ri 's/^Listen 80$/Listen 8081/' /etc/apache2/ports.conf \
 && sed -ri 's/:80>/:8081>/' /etc/apache2/sites-available/000-default.conf

# AllowOverride All is what makes the high tier (.htaccess override) possible. Leaving it at None
# would silently turn that tier into an impossible puzzle.
RUN printf '%s\n' \
    '<Directory /var/www/html>' \
    '    Options Indexes FollowSymLinks' \
    '    AllowOverride All' \
    '    Require all granted' \
    '</Directory>' \
    > /etc/apache2/conf-available/pentarange.conf \
 && a2enconf pentarange

COPY htaccess /var/www/html/.htaccess
COPY index.php /var/www/html/index.php

EXPOSE 8081