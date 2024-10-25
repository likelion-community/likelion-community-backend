function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // 이름이 'name='과 같은지 확인
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Ajax 설정에서 CSRF 토큰을 헤더에 추가
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!/^(GET|HEAD|OPTIONS|TRACE)$/.test(settings.type) && !this.crossDomain) {
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});
$('#verify-photo-button').on('click', function() {
    const formData = new FormData();
    formData.append('verification_photo', $('#id_verification_photo')[0].files[0]);

    $.ajax({
        url: '/signup/verify_photo/',
        type: 'POST',
        headers: {
            'X-CSRFToken': csrftoken
        },
        data: formData,
        processData: false,
        contentType: false,
        success: function(response) {
            if (response.is_valid) {
                alert('사진 인증 성공!');
            } else {
                alert('사진 인증 실패. 다시 시도해 주세요.');
            }
        },
        error: function(xhr, status, error) {
            alert('유효성 검사 중 오류가 발생했습니다. 다시 시도해 주세요.');
        }
    });
});
