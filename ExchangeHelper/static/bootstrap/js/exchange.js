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

$(document).on('click', 'button[name=calculate]', convert);

function fromUah(amount, currency) {
    rate = ExchangeRates[currency][operation];
    converted = amount * rate;
    return (converted).toFixed(4)
}

function toUah(amount, currency) {
    rate = ExchangeRates[currency][operation];
    converted = amount / rate;
    return (converted).toFixed(4)
}