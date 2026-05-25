/**
 * Логи только на localhost или при ?debug=1.
 * На staging/prod консоль не засоряется и не светит API/данные.
 */
const AppDebug = (function () {
    const host = typeof location !== 'undefined' ? location.hostname : '';
    const enabled =
        host === 'localhost' ||
        host === '127.0.0.1' ||
        (typeof location !== 'undefined' && /[?&]debug=1(?:&|$)/.test(location.search));

    if (!enabled && typeof console !== 'undefined') {
        const noop = function () {};
        ['log', 'debug', 'info', 'warn', 'error', 'trace', 'dir', 'table'].forEach((m) => {
            if (typeof console[m] === 'function') {
                console[m] = noop;
            }
        });
    }

    return {
        enabled,

        log(...args) {
            if (enabled) console.log(...args);
        },

        warn(...args) {
            if (enabled) console.warn(...args);
        },

        error(...args) {
            if (enabled) console.error(...args);
        },

        /** Сообщение для alert/UI без деталей бэкенда на проде */
        userMessage(context, err) {
            if (enabled && err) {
                return `${context}: ${err.message || err}`;
            }
            return context;
        }
    };
})();
