from flask import Flask, jsonify, request, render_template
from views.user import register_mobile, verify_mobile, register_user, login_user,\
    forgot_password, reset_password, edit_profile, get_profile
from views.device import device_operation, register_device
from views.search_user import search_user, show_all_users
from views.friend_operation import send_friend_request, respond_friend_request,\
    get_friend_requests, get_friends, remove_friend, friend_operation
from views.circle_operation import circle_operation, create_circle, add_members, remove_member,\
    make_admin, leave_circle, edit_circle, delete_circle, get_circles
from views.sync_contact import sync_contacts
from views.image_operation import image_operation, upload_user_image, upload_circle_image
from views.common.image import upload_image

app = Flask(__name__)
# Maximum size for file upload, 5 MB
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024


@app.route('/')
@app.route('/api')
def index():
    return '<h2>Hello !!!<br> mi-Approval API, v1.0</h2>'


@app.errorhandler(404)
def page_not_found(error):
    return jsonify(status=0, message='404. API Not Found')


@app.route('/api/user/search/<string:pattern>')
def user_search(pattern):
    return search_user(pattern)


@app.route('/api/mobile/register', methods=['POST'])
def mobile_register():
    return register_mobile()


@app.route('/api/mobile/verify', methods=['POST'])
def mobile_verify():
    return verify_mobile()


@app.route('/api/user/register', methods=['POST'])
def user_register():
    return register_user()


@app.route('/api/user/login', methods=['POST'])
def user_login():
    return login_user()


@app.route('/api/device/register', methods=['POST'])
def device_register():
    return device_operation(register_device)


@app.route('/api/user/password/forgot', methods=['POST'])
def password_forgot():
    return forgot_password()


@app.route('/api/user/password/reset', methods=['POST'])
def password_reset():
    return reset_password()


@app.route('/api/user/profile/edit', methods=['POST'])
def profile_edit():
    return edit_profile()


@app.route('/api/user/profile/get', methods=['POST'])
def profile_get():
    return get_profile()


@app.route('/api/user/image/upload/<string:token>', methods=['POST'])
def user_image_upload(token):
    return image_operation(token, upload_user_image)


@app.route('/api/friend_request/send', methods=['POST'])
def friend_request_send():
    return friend_operation(send_friend_request)


@app.route('/api/friend_request/respond', methods=['POST'])
def friend_request_respond():
    return friend_operation(respond_friend_request)


@app.route('/api/friend_request/get', methods=['POST'])
def friend_request_get():
    return friend_operation(get_friend_requests)


@app.route('/api/friend/get', methods=['POST'])
def friends_get():
    return friend_operation(get_friends)


@app.route('/api/friend/remove', methods=['POST'])
def friend_remove():
    return friend_operation(remove_friend)


@app.route('/api/circle/create', methods=['POST'])
def circle_create():
    return circle_operation(create_circle)


@app.route('/api/circle/edit', methods=['POST'])
def circle_edit():
    return circle_operation(edit_circle)


@app.route('/api/circle/delete', methods=['POST'])
def circle_delete():
    return circle_operation(delete_circle)


@app.route('/api/circle/member/add', methods=['POST'])
def circle_member_add():
    return circle_operation(add_members)


@app.route('/api/circle/member/remove', methods=['POST'])
def circle_member_remove():
    return circle_operation(remove_member)


@app.route('/api/circle/member/leave', methods=['POST'])
def circle_member_leave():
    return circle_operation(leave_circle)


@app.route('/api/circle/member/make_admin', methods=['POST'])
def circle_member_make_admin():
    return circle_operation(make_admin)


@app.route('/api/circle/get_all', methods=['POST'])
def circle_get_all():
    return circle_operation(get_circles)


@app.route('/api/circle/image/upload/<string:token>', methods=['POST'])
def circle_image_upload(token):
    return image_operation(token, upload_circle_image)


@app.route('/api/contact/sync', methods=['POST'])
def contact_sync():
    return sync_contacts()


@app.route('/image/upload', methods=['GET', 'POST'])
def image_upload():
    if request.method == 'POST':
        try:
            return upload_image(3, None, 1)
        except Exception as e:
            message = format(e)
        return jsonify(status=0, message=message)
    return render_template('index.html')


@app.route('/api/test', methods=['GET', 'POST'])
def test():
    # return send_data_multiple([4,11,0], 'HELLO JAMLO')
    return show_all_users()


if __name__ == '__main__':
    app.debug = True
    app.run()
