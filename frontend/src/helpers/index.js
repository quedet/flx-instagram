const debounce = function (fn, delay=10) {
    let timeoutId = null;

    return () => {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(fn, delay);
    };
};

export default debounce;
