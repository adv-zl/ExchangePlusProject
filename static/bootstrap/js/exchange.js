function handleOperationChange() {
	if ($(this).val() == 's') {
		$('.val_1_desc').html('Сумма для покупки-получения');
		$('.val_2_desc').html('Сумма для продажи-выдачи, грн');
		$('.cur_1_desc').html('Валюта для покупки-получения');
		$('.cur_2_desc').html('Валюта для продажи-выдачи');
	} else {
		$('.val_1_desc').html('Сумма для продажи-выдачи');
		$('.val_2_desc').html('Сумма для покупки-получения, грн');
		$('.cur_1_desc').html('Валюта для продажи-выдачи');
		$('.cur_2_desc').html('Валюта для покупки-получения');
	}
}

$(document).on('click', 'input[name="operation"]', handleOperationChange);

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
		alert('Валюты одинаковые');
		return false;
	}
	// Можно задоджить если дать изначальное значение инпуту или аттрибут required
	if (c.val_1 == 0 || c.val_1 == null) {
		alert('Введите значение');
		return false;
	}
	// Все валюты сравниваются с гривной. Соответственно,
	if (operation == 'b'){
		result = UahToCur(c.val_1, c.cur_1)
	}
	else {
		if (c.cur_1 == 'uah') {
			result = CurFromUah(c.val_1, c.cur_2)
		}
		else if (c.cur_2 == 'uah') {
			result = UahFromCur(c.val_1, c.cur_1, c.cur_2)
		} else {
			result = CurFromUah(UahFromCur(c.val_1, c.cur_1, c.cur_2), c.cur_2)
		}
	}
	$('.val_2').val(result)
}

$(document).on('click', 'button[name=calculate]', convert);
// ПОКУПКА гривень
function CurToUah(amount, currency, currency_2) {
	rate = ExchangeRates[currency]['b']; // Сколько гривень дадут за 1 валюту
	converted = amount / rate;
	if (currency_2 == "uah") {
        if (amount > AvailableFunds[currency_2]) {
            alert("Нехватка " + currency_2 + " в кассе!");
        } else {
            return (converted).toFixed(2)
        }
    }else {
            return (converted).toFixed(4)
	}
}
// покупка чего-то за гривны
function UahToCur(amount, currency) {
	rate = ExchangeRates[currency]['s']; // Сколько гривень стоит 1 валюта
	converted = amount * rate;
	if ( amount > AvailableFunds[currency]) {
		alert("Нехватка " + [currency] + " в кассе!!!");
	} else {
		return (converted).toFixed(2)
	}
}
//ПРОДАЖА
function CurFromUah(amount, currency) {
	rate = ExchangeRates[currency]['s']; // Сколько гривень стоит 1 валюта
	converted = amount / rate;
	if (converted > AvailableFunds[currency]) {
		alert("Не хватает на  " + (converted).toFixed(2) +" "+ currency + " в кассе!");
	} else {
            return (converted).toFixed(2)
	}
}
function UahFromCur(amount, currency, currency_2) {
	rate = ExchangeRates[currency]['b']; // Сколько гривень дадут за 1 валюту
	converted = amount * rate;
	if (currency_2 == 'uah'){
		if (converted > AvailableFunds[currency_2]) {
			alert("Не хватает на  " + (converted).toFixed(2) +" "+ currency_2 + " в кассе!!");
		} else {
			return (converted).toFixed(2)
		}
	}
	else {
		return (converted).toFixed(2)
	}

}