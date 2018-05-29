echo Some useful stuff to run before comitting to git
echo
echo running unit tests:
nosetests tests/test*.py
echo
echo
echo Lint summary
find .  -name "*.py" | xargs /usr/local/bin/pylint
echo done

