(for file in $(find . -name "*.py" | xargs); do
    echo ''
    echo '# ================='
    echo '# FILENAME:' $file
    echo '# ================='
    echo ''
    cat $file
done) > gui.txt
