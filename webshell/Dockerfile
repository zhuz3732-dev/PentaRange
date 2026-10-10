# Apache + mod_php. This is the service that actually executes what the upload challenges produce.
# It exists because "the file landed on disk" is not an exploit: .htaccess only means something to
# a server that honours it, and a webshell only means something to a server that runs it.
FROM php:8.2-apache

# The module is named `php`, not `php8`. The official images load mod_php via
# /etc/apache2/mods-available/php.load, so `a2enmod php8` fails with "Module php8 does not exist".
# The port remap appends to ports.conf instead of rewriting the existing `Listen 80` line, which
# keeps this from breaking when the Debian base image changes its defaults.
RUN a2enmod rewrite headers \
 && printf '\nListen 8081\n' >> /etc/apache2/ports.conf \
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
