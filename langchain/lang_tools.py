import dotenv
from langchain.tools import tool
from ..database import Database
import requests
from .config import Config

graphql_api_url = 'https://jh4rgdondlpgd6a6w5dtyyrg6m0dbudj.lambda-url.ap-south-1.on.aws/shop-api'

# global bearer_token 
bearer_token_set = False
vendure_auth_token=""



# @tool
# def products(search_input):
#     """
#     Useful when you need to answer questions
#     about the items available like fish,meat.the price of items,description of the item. 
#     Not useful for answering questions about anything other than that.
#     do not pass the entire question as input to the tool. 
#     For instance,
#     if the question is "fish",
#     the input should be " ",
#     if the question is "fish mahi mahi",
#     the input should be "mahi mahi"
#     """

#     products_data = {
#         "input": {
#         "term": search_input
#         }

#         }

   
        

#     # Define your GraphQL query to fetch products
#     products_query = """
#             query Query($input: SearchInput!) {
#                 search(input: $input) {
#                     items {
#                         productName
#                         description
#                         price {
#                             ... on SinglePrice {
#                                 value
#                             }
#                         }
#                         productId
#                     }
#                 }
#             }

#         """
    
    
#     # Send a POST request to the GraphQL API with the query
#     response = requests.post(graphql_api_url, json={'query': products_query, 'variables': products_data})

#     # Check if the request was successful
#     if response.status_code == 200:
#             # Parse the JSON response
#             data = response.json()

#             # Extract product information from the response
#             products_list = []
#             items = data.get('data', {}).get('search', {}).get('items', [])
#             for item in items:
#                 product_name = item.get('productName', '')
#                 description = item.get('description', '')
#                 price = item.get('price', {}).get('value', '')
#                 products_list.append({'productName': product_name, 'description': description, 'price': price})
#             return products_list

#     else:
#             print("Failed to fetch products from API:", response.text)
#             return []
    

@tool
def instock(search_input):
    """
    For instance,the search input should be the name of fish/meat,dont pass quantity or price with it.
    if the question is "is 100 g of kilimeen available?" the search input should be "kilimeen",
    if the question is "800 g of chala available?" the search input should be "chala",
    if the question is "chala and kilimeen" the search input should be"chala" "kilimeen" separately.
    if the question is " karimeen 700g + mahi mahi 300 g",the search input should be "karimeen + mahi mahi",
    if the question is "thirandi for 20,000",the search input should be "thirandi",
    if the question is "Kilimeen 500g + Mutton 500g priced at 75000 and Chala/Mathi/Sardine priced at 16000",the search input is "kilimeen+mutton and chala".
    if the question is to "show the menu or available fishes or fishes", then the search input should be null. eg: " ".
    """
    instock_data = {
        "options": {
          "filter": {
            "name": {
              "contains":search_input
            }
         },
          "sort": {
            "name": "DESC"
          }
        }
}
    


    # Define your GraphQL query to fetch products
    instock_query = """
            query Products($options: ProductListOptions) {
            products(options: $options) {
              totalItems
              items {
              
                variantList {
                  totalItems
                  items {
                    id
                    name
                    productId
                    price
                    discountPrice
                    stockLevel
                  }
                }
              }
            }
          }
            
        """
    
    # Send a POST request to the GraphQL API with the query
    response = requests.post(graphql_api_url, json={'query': instock_query, 'variables': instock_data})
    if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            
            # Extract product information from the response
            instock_list = []
            items = data.get('data', {}).get('products', {}).get('items', [])
            for item in items:
                for variant in item.get('variantList', {}).get('items', []):
                    stock_item = variant.get('name', '')
                    product_v_id = variant.get('id', '')
                    item_price = variant.get('price', '')
                    instock_list.append({'name': stock_item, 'price': item_price, 'id': product_v_id})
            
            return instock_list
                    
             
    else:
            print("Failed to fetch products from API:", response.text)
            return []   



@tool
def add_to_cart(search_input,quantity):
    """
    first cart_query should be invoked and the data recieved from this should be used for add_item_mutation query.
    add the items they want to the cart. dont invoke this unneccessarly.
    the search input should be just names of the fishes. dont add combo or other terms with it.
    do not give price and weight as the search input. the quantity should be an interger value. dont consider units.
    if the question is "Kilimeen 500g + Mutton 500g" the search input should be kilimeen +mutton,and quantity(500g)
    if the question is "Chala/Mathi/Sardine priced at 16000" ,the search input should be "Chala/Mathi/Sardine",
    if the question is "needs 800 g of chala",The search input should be chala and its quantity 800.
    if the question is"Chala/Mathi/Sardine - 250g",The search input should be chala and its quantity 250
    Example message format is in below :message = {"session_id":session_id,"message":message}Please use the session id from the above example as session id
    """
    # global bearer_token, bearer_token_set
    Config.bearer_token = Database.get_bearer_token(Config.session_id)
    print("____printing session_id with bearer_token______:",Config.session_id,Config.bearer_token)
   
    instock_data = {
    "searchInput": {
      "term": search_input
    }
  }


    # Define your GraphQL query to fetch products
    instock_query = """
            query Search($searchInput: SearchInput!) {
              search(input: $searchInput) {
                totalItems
                items {      
                  productVariantId
                }
              }
            }
            
        """
    
    # Send a POST request to the GraphQL API with the query
    response = requests.post(graphql_api_url, json={'query': instock_query, 'variables': instock_data})

    # Check if the request was successful
    if response.status_code == 200:
            # Parse the JSON response
            data = response.json()

            # Extract product information from the response
            
            items = data.get('data', {}).get('search', {}).get('items', [])
            for item in items:
                 product_v_id = item.get('productVariantId', '')
                  
                    
             
            cart_items={  
                    "productVariantId": product_v_id,
                    "quantity": int(quantity)
            }
                # graphql query to add items to cart
            add_item_mutation="""
                    mutation AddItemToOrder($productVariantId: ID!, $quantity: Int!) {
                        addItemToOrder(productVariantId: $productVariantId, quantity: $quantity) {
                            ... on Order {
                                    total
                                    taxSummary {
                                        taxTotal
                                    }
                                }
                        }
                    }
            
            """
            
            if Config.bearer_token == None:
                response = requests.post(graphql_api_url, json={'query': add_item_mutation, 'variables': cart_items})
                if response.status_code == 200:
                    Config.bearer_token = response.headers.get('vendure-auth-token')
                    print("!!!!!!!!!!token :: \n", Config.bearer_token)
                    Database.update_bearer_token(Config.session_id, Config.bearer_token) 
                    
                    data = response.json()
                    order_data=data.get('data',{}).get('addItemToOrder',{})
                    return {'order_data':order_data,"bearer_token":Config.bearer_token}
            else:
                    token_headers = {
                        'Authorization': f'Bearer {Config.bearer_token}',
                        'Content-Type': 'application/json'
                    }
                    response = requests.post(graphql_api_url, json={'query': add_item_mutation, 'variables': cart_items}, headers=token_headers)
                    Database.update_bearer_token(Config.session_id, Config.bearer_token) 
                    if response.status_code == 200:
                        data = response.json()
                        order_data=data.get('data',{}).get('addItemToOrder',{})
                        return {'order_data':order_data,"bearer_token":Config.bearer_token}
            # update_bearer_token(session_id, bearer_token)  
  

@tool
def setCustomerForOrder(email_Address,first_Name,last_Name,phone_Number):
    """
    this tool should be invoked after adding items to cart
    this is used to set the mandatory details of the customer such as firstName, lastName, emailAddress and phoneNumber.
    strictly collect personaly details like firstName, lastName, emailAddress and phoneNumber of customer.
    """
    customer_data = {
   "input": {
    "emailAddress": email_Address,
    "firstName": first_Name,
    "lastName": last_Name,
    "phoneNumber": phone_Number
  }

}
    


    # Define your GraphQL query to fetch products
    customer_detail = """
            mutation Mutation($input: CreateCustomerInput!) {
  setCustomerForOrder(input: $input) {
    ... on Order {
      customer {
        firstName
        emailAddress
        lastName
        phoneNumber
      }
    }
  }
} 
"""
    
    # Send a POST request to the GraphQL API with the query
    # global bearer_token
    token_headers = {
                        'Authorization': f'Bearer {Config.bearer_token}',
                        'Content-Type': 'application/json'
                    }
    print("token_headers :: ", token_headers)
    response = requests.post(graphql_api_url, json={'query': customer_detail, 'variables': customer_data}, headers=token_headers)
    if response.status_code == 200:
            # Parse the JSON response
            data = response.json()
            print("set customer data :: ", data)
            # Extract product information from the response
            customer_detail_list = []
            items = data.get('data', {}).get('search', {}).get('items', [])
            for item in items:
                # product_id = item.get('productId', '')
                first_name=item.get('firstName','')
                last_name=item.get('lastName','')
                email=item.get('emailAddress','')
                phn_no=item.get('phoneNumber')
                customer_detail_list.append({'firstName':first_name,'lastName': last_name,'emailAddress':email,'phoneNumber':phn_no})
            print('customer_detail_list :: ',customer_detail_list)

            return customer_detail_list

    else:
            print("Failed to fetch products from API:", response.text)
            return []   


@tool
def setOrderShippingAddress(street_Line1,postal_Code):

    """
    this tool should be invoked after setCustomerForOrder tool.
    this is used to set the mandatory details of the customer's shipping address such as streetLine1, postalCode.
    """
    address_data = {

     "input": {
    "countryCode": "IND",
    "streetLine1": street_Line1,
    "postalCode": postal_Code
  }

}

    # Define your GraphQL query to fetch products
    address_detail = """
   mutation Mutation($input: CreateAddressInput!) {
  setOrderShippingAddress(input: $input) {
    ... on Order {
      shippingAddress {
        countryCode
        streetLine1
        postalCode
      }
    }
  }
}     
"""
    
    # Send a POST request to the GraphQL API with the query
    # global bearer_token
    token_headers = {
                        'Authorization': f'Bearer {Config.bearer_token}',
                        'Content-Type': 'application/json'
                    }
    response = requests.post(graphql_api_url, json={'query': address_detail, 'variables': address_data}, headers=token_headers)
    if response.status_code == 200:
        try:
            data = response.json()
            shipping_address_list = []
            items = data.get('data', {}).get('setOrderShippingAddress', {}).get('shippingAddress', {})
            address = items.get('streetLine1', '')
            p_code = items.get('postalCode', '')
            shipping_address_list.append({'streetLine1': address, 'postalCode': p_code})
            return shipping_address_list
        except Exception as e:
            print("Error parsing setOrderShippingAddress response:", e)
            return []
    else:
        print("Failed to set order shipping address:", response.text)
        return []






@tool
def getAllEligibleShippingMethods():

    """
    this tool should be invoked after invoking setOrderShippingAddress.
    this is used to get the avilable shipping methods and also setting the chosen shipping method.
    first eligible_ShippingMethods_query should be invoked and should ask the user to chose from the returned shipping methods.
    after this setOrderShippingMethod should be invoked by passing the shipping_method_id of the shipping method selected by the user.
    once the shipping method is set return the order_details data and display it to the customer.
    """
    eligible_ShippingMethods_query= """
    query Query {
    eligibleShippingMethods {
        code
        id
        description
        name
        metadata
        price
        priceWithTax
    }
}   
            """
    # global bearer_token
    print(Config.bearer_token)
    token_headers = {
                            'Authorization': f'Bearer {Config.bearer_token}',
                            'Content-Type': 'application/json'
                        }
    print("token_headers :: ", token_headers)
    response = requests.post(graphql_api_url, json={'query': eligible_ShippingMethods_query}, headers=token_headers)
    if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                shipping_method_list = []
                items = data.get('data', {}).get('eligibleShippingMethods', [])
                for item in items:
                    # product_id = item.get('productId', '')
                    shipping_method_id=item.get('id','')
                    shipping_method_name=item.get('name','')
                    shipping_method_price=item.get('price','')
                    shipping_method_list.append({'id':shipping_method_id,'name':shipping_method_name,'price':shipping_method_price})
                return shipping_method_list

    else:
            print("Failed to fetch products from API:", response.text)
            return []  




@tool
def setShippingMethodToOrder(shipping_method_id : int):
    """
    This tool is invoked after the user chooses the shipping method. 
    the input is the user selected shipping_method_id which is a single integer value .
    this tool is used to set the shipping method selected by the user for the order. 
    once the shipping method is set return the order_details data and display it to the customer.
    For instance,if the user asks for standard shipping ,the input is the corresponding shipping_method_id
    """
    print("######shipping_id######",shipping_method_id)

    shipping_method_data = {
    "shippingMethodId": int(shipping_method_id)
    }

    # Define your GraphQL query to fetch products
    set_OrderShippingMethod_query = """
    mutation Mutation($shippingMethodId: [ID!]!) {
    setOrderShippingMethod(shippingMethodId: $shippingMethodId) {
        ... on Order {
        actualTotal
        customer {
            firstName
            lastName
            emailAddress
            phoneNumber
        }
        lines {
            productVariant {
            name
            }
            quantity
        }
        shippingAddress {
            countryCode
            postalCode
            streetLine1
        }
        shippingLines {
            shippingMethod {
            name
            }
        }
        total
        totalQuantity
        totalWithTax
        }
    }
}
            
        """
    
    # Send a POST request to the GraphQL API with the query
    token_headers = {
                        'Authorization': f'Bearer {Config.bearer_token}',
                        'Content-Type': 'application/json'
                    }
    print("token_headers :: ", token_headers)
    response = requests.post(graphql_api_url, json={'query': set_OrderShippingMethod_query, 'variables': shipping_method_data}, headers=token_headers)
    if response.status_code == 200:
        try:
            data = response.json()
            order_details = data.get('data', {}).get('setOrderShippingMethod', {})
            return order_details
        except Exception as e:
            print("Error parsing setOrderShippingMethod response:", e)
            return {}
    else:
        print("Failed to set order shipping method:", response.text)
        return {}
           

@tool
def transitionOrderToCompletion():
      
    """"
    This method should be invoked after setting the setShippingMethodToOrder.
    It will transition the order to the next state in the workflow.
    This tool transitions the order to the "CashOnDelivery" state.
    """
    state = {
  "state": "CashOnDelivery"
}


    transition_state= """
                mutation Mutation($state: String!) {
  transitionOrderToState(state: $state) {
    ... on OrderStateTransitionError {
      message
      transitionError
    }
    ... on Order {
      lines {
        order {
          lines {
            order {
              id
            }
          }
        }
      }
      state
      customer {
        id
        user {
          id
        }
      }
    }
  }
}
    """

    # global bearer_token
    print(Config.bearer_token)
    token_headers = {
                            'Authorization': f'Bearer {Config.bearer_token}',
                            'Content-Type': 'application/json'
                        }
    print("token_headers :: ", token_headers)
    response = requests.post(graphql_api_url, json={'query': transition_state,'variables': state}, headers=token_headers)
    if response.status_code == 200:
                # Parse the JSON response
                data = response.json()
                id = data.get('data', {}).get('transitionOrderToState', {})
                Config.bearer_token =None
 