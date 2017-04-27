function setupRates() {
    // Имитируем значения которые якобы пришли с бэкенда. 
    // Тут должен быть код который откуда-то из дом ноды заберет инфу или сделает аякс реквест.

    // Экшоли, в пизду целочисленные значения, мы ж не лохи, пусть обсчитывается с точкой и приводится
    var rates = {
        usd: { b: 26.63, s: 27.00 },
        eur: { b: 29.00, s: 30.00 },
        rub: { b: .47, s: .49 },
        cad: { b: 0, s: 0 },
        chf: { b: 26.79, s: 27.00 },
        gbp: { b: 34.15, s: 34.30 },
        pln: { b: 6.86, s: 7.00 },
    }
    window.ExchangeRates = rates;// и сохраняем в глобальном обьекте
}
$(document).ready(setupRates);


function handleOperationChange() {
    if ($(this).val() == 's') {
        $('.val_1_desc').html('Вносимая сумма(заплатит покупатель)');
        $('.val_2_desc').html('Полученная сумма(получит покупатель)');
        $('.cur_1_desc').html('Выберите валюту для покупки');
        $('.cur_2_desc').html('Выберите вносимую валюту');
    } else {
        $('.val_1_desc').html('Введите сумму для покупки(получит покупатель)');
        $('.val_2_desc').html('Вносимая сумма(заплатит покупатель)');
        $('.cur_1_desc').html('Выберите валюту для покупки');
        $('.cur_2_desc').html('Выберите вносимую валюту');
    }
}

$(document).on('click','input[name="operation"]', handleOperationChange);

function convert(e) {
    e.preventDefault();
    window.operation = $('input[name="operation"]:checked').val();
    var result;
    // вычитание всегда возвращает число, самый простой способ привести типы
    var c/* conditions */ = {
        val_1: $('.val_1').val() - 0,
        cur_1: $('.cur_1').val(),
        cur_2: $('.cur_2').val(),
    }
    console.log(c);
    // Валидация
    if (c.cur_1 == c.cur_2) {
        alert('Валюты одинаковые')
        return false;
    }
    // Можно задоджить если дать изначальное значение инпуту или аттрибут required
    if (c.val_1 == null) {
        alert('Введите значение');
        return false;
    }
    // Все валюты сравниваются с гривной. Соответственно, 
    if (c.cur_1 == 'uah') {
        result = toUah(c.val_1, c.cur_2)
    }
    else if (c.cur_2 == 'uah') {
        result = fromUah(c.val_1, c.cur_1)
    } else {
        result = toUah(fromUah(c.val_1, c.cur_1), c.cur_2)
    }
    $('.val_2').val(result)
}

$(document).on('click', 'button[name=check]', convert);

function fromUah(amount, currency) {
    rate = ExchangeRates[currency][operation];
    converted = amount * rate;
    return (converted).toFixed(2)
}

function toUah(amount, currency) {
    rate = ExchangeRates[currency][operation];
    converted = amount / rate;
    return (converted).toFixed(2)
}