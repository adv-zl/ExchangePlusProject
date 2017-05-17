

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
	if (c.val_1 == null) {
		alert('Введите значение');
		return false;
	}

	// Все валюты сравниваются с гривной. Соответственно,
	if (operation == 'b') {
		if (c.cur_1 == 'uah') {
			result = CurToUah(c.val_1, c.cur_2)
		}
		else if (c.cur_2 == 'uah') {
			result = UahToCur(c.val_1, c.cur_1)
		} else {
			result = CurToUah(UahToCur(c.val_1, c.cur_1), c.cur_2)
		}
	} else {
		if (c.cur_1 == 'uah') {
			result = CurFromUah(c.val_1, c.cur_2)
		}
		else if (c.cur_2 == 'uah') {
			result = UahFromCur(c.val_1, c.cur_1)
		} else {
			result = CurFromUah(UahFromCur(c.val_1, c.cur_1), c.cur_2)
		}
	}

	$('.val_2').val(result)
}

$(document).on('click', 'button[name=calculate]', convert);

function CurToUah(amount, currency) {
	rate = ExchangeRates[currency]['b']; // Сколько гривень дадут за 1 валюту
	converted = amount / rate;
	return (converted).toFixed(4)
}
function UahToCur(amount, currency) {
	rate = ExchangeRates[currency]['s']; // Сколько гривень стоит 1 валюта
	converted = amount * rate;
	return (converted).toFixed(4)
}
function CurFromUah(amount, currency) {
	rate = ExchangeRates[currency]['s']; // Сколько гривень стоит 1 валюта
	converted = amount / rate;
	return (converted).toFixed(4)
}
function UahFromCur(amount, currency) {
	rate = ExchangeRates[currency]['b']; // Сколько гривень дадут за 1 валюту
	converted = amount * rate;
	return (converted).toFixed(4)
}