import time

products = env['product.product'].with_context(lang='en_US').search([
    '|',
        ('name', '=', 'Funghi'),
        '|',
            ('name', '=', 'Coca-Cola'),
            ('name', '=', 'Lunch Maki 18pc'),
])
if not products:
    products = env['product.product'].with_context(lang='en_US').search([
        '|',
            ('name', '=', 'Aperol Spritz'),
            '|',
                ('name', '=', 'Cheeseburger'),
                ('name', '=', 'Sandwich Mozzarella'),
    ])
print(f'Using products {products}')

class PosSimulator:
    def __init__(self, pos_config):
        self.pos_config = pos_config
        self.pos_session = self.pos_config.current_session_id
        login_numbers = self.request_login_numbers()
        self.login_numbers = login_numbers.split(', ') if login_numbers else []
        if not self.login_numbers:
            raise Exception('no POS browser with debug enabled found')
        self.pos_browsers = [POSBrowser(self, n) for n in self.login_numbers]

    def _notify(self, command, data=None, commit=True, login_number=None):
        if data is None:
            data = {}
        data['command'] = command
        data['pos_session_id'] = self.pos_session.id
        if login_number:
            data['login_number'] = login_number
        self.pos_config._notify('SIMULATE_COMMAND', data)
        if commit:
            env.cr.commit()

    def notify_synchronisation(self, login_number):
        self.pos_config.notify_synchronisation(self.pos_session.id, login_number)

    def request_login_numbers(self):
        self.pos_config.active_session_login_numbers = False
        self._notify('login_number')
        time.sleep(10)
        return self.pos_config.active_session_login_numbers

    def simulate(self):
        print(f'POS browser sessions with run ids / login numbers found: {", ".join(self.pos_simulator.login_numbers)}')
        print(f'POS Floors: {", ".join([f.name for f in self.pos_config.floor_ids])}')
        floor = self.pos_config.floor_ids[0]
        #self.fill_floor(floor)
        #self.empty_floor(floor)
        for table in floor.table_ids:
            self.create_ticket(table)
            self.goto_screen(table, 'ProductScreen')
            self.add_products(table)
            self.pos_config.notify_synchronisation(self.pos_session.id, 0)
            time.sleep(2)
            self.validate_ticket(table)
            time.sleep(2)
            self.goto_screen(table, 'FloorScreen')
            time.sleep(1)
        self.pos_config.notify_synchronisation(self.pos_session.id, 0)
    
class POSBrowser(object):
    def __init__(self, pos_simulator, login_number):
        self.pos_simulator = pos_simulator
        self.login_number = login_number

    def _notify(self, command, data=None, commit=True):
        if command == 'login_number':
            login_number = None
        else:
            login_number = self.login_number
        self.pos_simulator._notify(command, data, commit=commit, login_number=login_number)

    def notify_synchronisation(self, login_number=None):
        if login_number is None:
            login_number = self.login_number
        self.pos_simulator.notify_synchronisation(login_number)

    def fill_floor(self, floor, table_count=1):
        for i, table in enumerate(floor.table_ids):
            if table_count and i >= table_count:
                break
            print(f'creating ticket on table {table.table_number} with login_number {self.login_number}')
            self.create_ticket(table)

    def empty_floor(self, floor):
        for table in floor.table_ids:
            print(f'deleting tickets on table {table.table_number} with login_number {self.login_number}')
            self.delete_tickets(table)

    def create_ticket(self, table):
        self._notify('create_ticket', {
                'customer_count': 1,
                'table_id': table.id,
        }, commit=False)

    def add_products(self, table):
        self._notify('add_products', {
                'product_ids': products.ids,
                'table_id': table.id,
        })

    def print_changes(self, table):
        self._notify('print_changes', {
                'table_id': table.id,
        })

    def delete_tickets(self, table):
        self._notify('delete_tickets', {
                'table_id': table.id,
        })

    def validate_ticket(self, table):
        self._notify('validate_ticket', {
                'table_id': table.id,
        })

    def goto_screen(self, table, screen_name):
        self._notify('goto_screen', {
                'screen_name': screen_name,
                'table_id': table.id,
        })

    #########################################################
    def create_tickets_with_products(self, tables, max_count=0):
        #print(f'Browser {self.login_number}: creating ticket on tables {tables.mapped('table_number')}')
        for i, table in enumerate(tables):
            print(f'Browser {self.login_number}: creating ticket on table {table.table_number}')
            self.create_ticket(table)
            self.goto_screen(table, 'ProductScreen')
            time.sleep(1)
            print(f'adding products on table {table.table_number}')
            self.add_products(table)
            self.notify_synchronisation(0)
            time.sleep(1)
            self.goto_screen(table, 'FloorScreen')
            time.sleep(1)
            self.notify_synchronisation(0)
            if max_count and i >= max_count:
                break

    def print_changes_for_tickets(self, tables, max_count=0):
        #print(f'Browser {self.login_number}: printing changes on tables {tables.mapped('table_number')}')
        for i, table in enumerate(tables):
            print(f'Browser {self.login_number}: printing changes on table {table.table_number}')
            self.print_changes(table)
            time.sleep(6)
            self.goto_screen(table, 'FloorScreen')
            time.sleep(1)
            if max_count and i >= max_count:
                break

    def validate_tickets(self, tables, max_count=0):
        #print(f'Browser {self.login_number}: validating ticket on tables {tables.mapped('table_number')}')
        for i, table in enumerate(tables):
            print(f'Browser {self.login_number}: validating ticket on table {table.table_number}')
            self.validate_ticket(table)
            time.sleep(2)
            self.goto_screen(table, 'FloorScreen')
            if max_count and i >= max_count:
                break

def main():

    pos_config = env['pos.config'].search([
            ('name', '=', '115 POS R'),
    ])
    if not pos_config:
        pos_config = env['pos.config'].browse(4)
    print(f'Using POS config {pos_config}')
    pos_simulator = PosSimulator(pos_config)
    pos_browsers = pos_simulator.pos_browsers
    print(f'Using POS browsers with login numbers {', '.join(b.login_number for b in pos_browsers)}')
    floor = pos_config.floor_ids[0]
    pos_browsers[0].empty_floor(floor)
    tables = floor.table_ids
    for n in range(80):
        for i, table in enumerate(tables):
            pos_browsers[i % len(pos_browsers)].create_tickets_with_products(table)
        #for i, table in enumerate(tables):
        #    pos_browsers[i % len(pos_browsers)].print_changes_for_tickets(table)
        #for i, table in enumerate(tables):
        #    pos_browsers[i % len(pos_browsers)].validate_tickets(table)
        for i, table in enumerate(tables):
            pos_browsers[i % len(pos_browsers)].delete_tickets(table)

main()
