import os
import sys
import requests
import arcade
import pprint


WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
WINDOW_TITLE = "MAP"
MAP_FILE = "map.png"


class GameView(arcade.Window):
    def setup(self):
        self.get_image()

    def on_draw(self):
        self.clear()
        arcade.draw_texture_rect(
            self.background,
            arcade.LBWH(
                (self.width - self.background.width) // 2,
                (self.height - self.background.height) // 2,
                self.background.width,
                self.background.height
            ),
        )

    def get_image(self):
        server_address = 'http://geocode-maps.yandex.ru/1.x/?'
        api_key = '8013b162-6b42-4997-9691-77b7074026e0'
        geocode = 'Москва'
        geocoder_request = f'{server_address}apikey={api_key}&geocode={geocode}&format=json'
        response = requests.get(geocoder_request)
        toponym_coodrinates = None
        if response:
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            '''
            pprint.pprint(json_response)
            '''
            toponym_coodrinates = toponym["Point"]["pos"]
        m = ["Волоколамское ш., 69, Москва", "3-я Песчаная ул., 2, стр. 12, Москва", "ул. Лужники, 24, стр. 1, Москва"]
        c = []
        for i in m:
            geocoder_request = f'{server_address}apikey={api_key}&geocode={i}&format=json'
            response = requests.get(geocoder_request)
            json_response = response.json()
            toponym = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
            c.append(toponym["Point"]["pos"].split())
        toponym_coodrinates = toponym_coodrinates.split()
        server_address = 'https://static-maps.yandex.ru/v1?'
        api_key = 'f3a0fe3a-b07e-4840-a1da-06f18b2ddf13'
        ll_spn = f'll={toponym_coodrinates[0]},{toponym_coodrinates[1]}&spn=1,1'
        pt = f"{c[0][0]},{c[0][1]},flag~{c[1][0]},{c[1][1]},flag~{c[2][0]},{c[2][1]},flag"
        map_request = f"{server_address}{ll_spn}&apikey={api_key}&pt={pt}"
        response = requests.get(map_request)
        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)
        with open(MAP_FILE, "wb") as file:
            file.write(response.content)
        self.background = arcade.load_texture(MAP_FILE)


def main():
    gameview = GameView(WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE)
    gameview.setup()
    arcade.run()
    os.remove(MAP_FILE)


if __name__ == "__main__":
    main()