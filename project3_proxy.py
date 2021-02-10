# project3_proxy.py
#
# ICS 32 Winter 2020
# Project #3: Jack of All Trades
#
# This is a proxy server, which you can run on your own computer.  It's a
# web server, so it's able to respond to HTTP requests, just like the Alpha
# Vantage API server.  However, instead of serving up its own data, it
# forwards requests to the Alpha Vantage API, then randomly introduces
# failures of various kinds.
#
# YOU DO NOT NEED TO READ OR UNDERSTAND THIS CODE, though you can certainly
# feel free to take a look at it.  YOU ALSO SHOULD NOT SUBMIT THIS CODE,
# as it is not part of your project; it's a tool to help you to test whether
# you've met the requirements around handling failures, by allowing you to
# reliably simulate them.

import http.client
import http.server
import json
import random
import urllib.error
import urllib.request



# The probability of success (i.e., that the response from Alpha
# Vantage is sent back as-is, without modification)
SUCCESS_PROBABILITY = 1.0

# When removing attributes from objects at random, this is the
# probability that any given attribute will be removed
RANDOM_ATTRIBUTE_REMOVAL_PROBABILITY = 1.0



class ProxyHandler(http.server.BaseHTTPRequestHandler):
    def __getattr__(self, name, default = None):
        if name.startswith('do_'):
            return self._handle_request
        else:
            raise AttributeError(name)


    def log_message(self, format, *args):
        pass


    def _handle_request(self):
        proxy_request = urllib.request.Request(f'https://www.alphavantage.co{self.path}')
        proxy_request.method = self.command

        for name, value in self.headers.items():
            if name.upper() == 'HOST':
                proxy_request.add_header('Host', 'www.alphavantage.co')
            elif name.upper() == 'CONTENT-LENGTH':
                request_content_length = int(value)
                proxy_request.data = self.rfile.read()
                proxy_request.add_header(name, value)
            else:
                proxy_request.add_header(name, value)

        try:
            with urllib.request.urlopen(proxy_request) as response:
                self._write_response(response)
        except urllib.error.HTTPError as e:
            self._write_error(e.code)


    def _write_response(self, response: http.client.HTTPResponse) -> None:
        if response.status == 200:
            if random.random() < SUCCESS_PROBABILITY:
                self._write_response_as_is(response)
            else:
                self._choose_failure_writer()(response)
        else:
            self._write_response_as_is(response)


    def _choose_failure_writer(self):
        failure_writers = []
        
        for attr in dir(self):
            if attr.startswith('_write_failure'):
                failure_writers.append(getattr(self, attr))

        return random.choice(failure_writers)


    def _write_failure_empty_data(self, response: http.client.HTTPResponse) -> None:
        self._write_response_content(response, None, 200, 'Writing empty data instead of what Alpha Vantage sent')


    def _write_failure_random_data(self, response: http.client.HTTPResponse) -> None:
        content = json.dumps(generate_random_dict()).encode(encoding = 'utf-8')
        self._write_response_content(response, content, 200, 'Writing random data instead of what Alpha Vantage sent')


    def _write_failure_missing_attribute_all_objects(self, response: http.client.HTTPResponse) -> None:
        try:
            json_content = remove_attribute_from_all(json.load(response))
            content = json.dumps(json_content).encode(encoding = 'utf-8')
            self._write_response_content(response, content, 200, 'Writing Alpha Vantage data with same attribute missing from all objects')
        except json.JSONDecodeError:
            self._write_failure_random_data(response)


    def _write_failure_randomly_missing_attributes(self, response: http.client.HTTPResponse) -> None:
        try:
            json_content = randomly_remove_attributes(json.load(response))
            content = json.dumps(json_content).encode(encoding = 'utf-8')
            self._write_response_content(response, content, 200, 'Writing Alpha Vantage data with random attributes missing throughout')
        except json.JSONDecodeError:
            self._write_failure_random_data(response)


    def _write_failure_404(self, response: http.client.HTTPResponse) -> None:
        self._write_error(404)


    def _write_failure_503(self, response: http.client.HTTPResponse) -> None:
        self._write_error(503)


    def _write_response_as_is(self, response: http.client.HTTPResponse) -> None:
        content = response.read()
        status = response.status
        self._write_response_content(response, content, status, 'Writing Alpha Vantage response as-is')


    def _write_response_content(
            self, response: http.client.HTTPResponse,
            content: bytes or None, status: int, log: str) -> None:
        self.send_response(status)

        wrote_length = False

        for name, value in response.getheaders():
            if name.upper() == 'CONTENT-LENGTH':
                if content is not None:
                    self.send_header(name, str(len(content)))

                wrote_length = True
            elif name.upper() in ['SERVER', 'DATE', 'TRANSFER-ENCODING']:
                continue
            else:
                self.send_header(name, value)

        if not wrote_length:
            if content is not None:
                self.send_header('Content-Length', str(len(content)))
            else:
                self.send_header('Content-Length', '0')

        self.end_headers()

        if content is not None:
            self.wfile.write(content)

        print(log)


    def _write_error(self, status: int) -> None:
        self.send_error(status)
        print(f'Writing HTTP error with status code {status}')



def generate_random_dict() -> dict:
    return generate_random_dict_at_depth(0)



def generate_random_dict_at_depth(depth: int) -> dict:
    d = {}

    for i in range(random.randrange(3, 10)):
        key = generate_random_string()
        
        if random.random() < 0.25 - (0.05 * depth):
            value = generate_random_dict_at_depth(depth + 1)
        else:
            value = generate_random_string()

        d[key] = value

    return d



def generate_random_string() -> str:
    s = ''

    for i in range(random.randint(6, 16)):
        s += chr(random.randint(65, 90))

    return s



def remove_attribute_from_all(d: dict) -> dict:
    if not 'Meta Data' in d:
        return d

    max_row_size = 0

    for key in d:
        if key != 'Meta Data' and type(d[key]) == dict:
            max_row_size = max(max_row_size, find_max_row_size(d[key]))

    to_remove = random.randrange(max_row_size)

    result = {}

    for key in d:
        if key == 'Meta Data':
            result[key] = d[key]
        else:
            result[key] = remove_attribute(d[key], to_remove)

    return result



def find_max_row_size(d: dict) -> int:
    if all_values_are_non_dicts(d):
        return len(d)
    else:
        max_row_size = 0
        
        for key in d:
            if type(d[key]) == dict:
                max_row_size = max(max_row_size, find_max_row_size(d[key]))

        return max_row_size



def remove_attribute(d: dict, index: int) -> dict:
    if all_values_are_non_dicts(d):
        result = {}
        
        for i, key in enumerate(d):
            if i != index:
                result[key] = d[key]

        return result
    else:
        result = {}

        for key in d:
            result[key] = remove_attribute(d[key], index)

        return result



def all_values_are_non_dicts(d: dict) -> bool:
    for key in d:
        if type(d[key]) == dict:
            return False

    return True



def randomly_remove_attributes(d: dict) -> dict:
    result = {}

    for key in d:
        if type(d[key]) == dict:
            result[key] = randomly_remove_attributes(d[key])
        elif random.random() >= RANDOM_ATTRIBUTE_REMOVAL_PROBABILITY:
            result[key] = d[key]

    return result



def run() -> None:
    print('Starting up ...')
    print()

    with http.server.HTTPServer(('localhost', 0), ProxyHandler) as server:
        host, port = server.server_address

        print('To connect your Project 3 to the proxy server instead of')
        print('the Alpha Vantage API, use the following partial URL:')
        print()
        print(f'    http://{host}:{port}')
        print()
        print('Press Ctrl+C to shut down')

        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('Shutting down ...')

    print('Goodbye!')



if __name__ == '__main__':
    run()