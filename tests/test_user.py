from unittest import TestCase, mock
from medblocks import User
from medblocks.EncryptionLayer import RSA

class UserTests(TestCase):
    def test_user_random(self):
        user = User("Sidharth", "9585841964")
        assert user.name == "Sidharth"
        assert user.phone == "9585841964"
        assert user.rsa is not None
        assert user.bigchain is not None
            
    def test_user_export(self):
        user = User("Sidharth", "9585841964")
        json = user.to_json()
        print(json)
        assert type(json) == str

    def test_import_user(self):
        string = r'{"name": "Sidharth", "phone": "9585841964", "rsa": {"public": "-----BEGIN PUBLIC KEY-----\nMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQDS6Sr8a0u17k3njgV4OGlUGWLk\ncWLogmfSP/y89pvFvwgzjTRQ/LbK7DGLkTvVsDCH5fxDhyIJTpqT069ICJ598n/Q\n/FUbiKiXNW/2GozgWJA4+lmrvZTHuTbhbfQZ0LhY+byYLHocz8WCAwBCzMwqAUiX\naoYzCC7Eb1DINCjo4wIDAQAB\n-----END PUBLIC KEY-----", "private": "-----BEGIN RSA PRIVATE KEY-----\nMIICXwIBAAKBgQDS6Sr8a0u17k3njgV4OGlUGWLkcWLogmfSP/y89pvFvwgzjTRQ\n/LbK7DGLkTvVsDCH5fxDhyIJTpqT069ICJ598n/Q/FUbiKiXNW/2GozgWJA4+lmr\nvZTHuTbhbfQZ0LhY+byYLHocz8WCAwBCzMwqAUiXaoYzCC7Eb1DINCjo4wIDAQAB\nAoGBAMw4XhkgQ6Ub5G9MA1vPM53tHuaYK+97JdBdiPnnyBmHygcwuPGaYdzHK4o6\nzLcy7SsJtGQmmvxsEh0Fofmb7um/K2IQB1yXv9FfXBcOSb36YUqgLnOMEG/MDtb4\n5UTJjs29h6RVrC10mR0nOQiMNpFy5FBSfVEYAGzy+FOEDI0BAkEA49zs5m1t/ry9\n9HDqY3NBdWXdx48FWcyehjp1D/uMamHYzx5JLWLeDmrRyEgzoaiDfhGGJBtvZkDG\ngHXOhAT3IwJBAOz0XCcZ1g+9rVlv+frCA3+564bb9zdZgy7osSzC3fFK1B/I/Zb7\nq82+skLgFD8cqBR6buFtXzeEtmjkStRoQ0ECQQC2PyAXGNUOFmWTmbBORIPJYuUk\nVEbCUP9FeoHge6AOAh6HYcDDlTznqRYKq3zoQkCRV3DDdlH+JbbeTdsUCmijAkEA\n7FujQG2JFRKCw9/qXrMAgnuV8GOh6VgkfrolYRzP/kxB46K9McnAye4aKpMSHxIa\nprKpv7s1a0+6FE8ERXPrAQJBANZK+KHTV2Iy4mMlxrPWFKdgJrbyYEhIEoCseL4f\nhL1N4V7W/LVySPoqchnFOhWu4byo/jtu0OHYNomiKKAoWnQ=\n-----END RSA PRIVATE KEY-----"}, "bigchain": {"public": "cE7PdpdnS9K5AftrzPMkDmxPnFr7apRGnNuokWoyFPy", "private": "2sD7RVzw3v4NT75eKSfm4Qk4z9zeceTciqzxU5pCxqzF"}}'
        user = User(json=string)
        assert user.name == "Sidharth"
        assert user.phone == "9585841964"
        assert user.rsa is not None
        assert user.bigchain is not None
    
    def test_write_json_to_database(self):
        pass

    def test_retrive_from_database(self):
        pass
    
    def test_register_on_bigchain(self):
        pass
    
    def test_retrive_from_bigchain(self):
        pass